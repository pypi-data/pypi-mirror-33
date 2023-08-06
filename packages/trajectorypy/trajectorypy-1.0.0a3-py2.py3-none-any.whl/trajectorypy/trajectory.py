#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import numpy as np
from io import StringIO
from filterpy.kalman import KalmanFilter

class TrajectoryFilter(KalmanFilter):
    """ A KalmanFilter implementation for a trajectory

    > The system's evolving state over time traces a path 
    > (a phase space trajectory for the system) through the high-dimensional space. 
    > The phase space trajectory represents the set of states 
    > compatible with starting from one particular initial condition, 
    > located in the full phase space that represents the set of states compatible with starting from any initial condition. 
    > https://en.wikipedia.org/wiki/Phase_space

    A phase space object this filter can track has its own size in a 2D space, and moves with a constant acceleration.

    Variances in P, Q, and R are calculated from the given object size to make configurations easier.
    Note that R is a simplified version, where only the highest order values are non zero.
    """
    
    DIM_X = 6
    DIM_Z = 2
    
    F_BASE = np.array([
        [1, 1, 0.5, 0, 0, 0],
        [0, 1, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0.5],
        [0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 1]
    ])
    
    H_BASE = np.array([
        [1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0]
    ])
    
    
    def __init__(self, x0, object_size, object_size_error_ratio=0.1, decay=0.1, coefficient=0.1):
        super(TrajectoryFilter, self).__init__(dim_x=TrajectoryFilter.DIM_X, dim_z=TrajectoryFilter.DIM_Z)
        self._object_size_error_ratio = object_size_error_ratio
        
        self.P = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, decay**2, 0, 0, 0, 0],
            [0, 0, decay**4, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, decay**2, 0],
            [0, 0, 0, 0, 0, decay**4]
        ])
    
        self.Q_BASE = np.array([
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, decay**4, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, decay**4]
        ])
    
        self.R_BASE = np.array([
            [coefficient**2, 0],
            [0, coefficient**2]
        ])

        self.F = TrajectoryFilter.F_BASE * 1
        self.H = TrajectoryFilter.H_BASE * 1

        self.update_object_size(object_size)

        # initialize
        self.x = np.array([x0]).T
        self.P[:3, :] *= self._variances[0]
        self.P[3:, :] *= self._variances[1]
        
    def update_object_size(self, new_object_size):
        """ update properties dependent on std_dev, variance, Q, and R
        """
        self._object_size = np.array([new_object_size[0], new_object_size[1]])

        # key statistical properties
        self._std_devs = self._object_size * self._object_size_error_ratio / 3
        self._variances = self._std_devs **2

        self.Q = self.Q_BASE * 1
        self.R = self.R_BASE * 1
        # for x
        self.Q[:3, :] *= self._variances[0]
        self.R[:1, :] *= self._variances[0]
        # for y
        self.Q[3:, :] *= self._variances[1]
        self.R[1:, :] *= self._variances[1]

    @property
    def object_size(self):
        return self._object_size

    @property
    def object_size_error_ratio(self):
        return self._object_size_error_ratio
    

class PhaseSpaceObject(object):
    """ PhaseSpaceObject moves, and leaves a trajectory.
    """

    _very_small_value = 0.000001

    def __init__(self, x0, object_size, object_size_error_ratio=0.5, decay=0.1, coefficient=0.5, maximum_heading_diff_allowed_in_pi=0.333):
        super(PhaseSpaceObject, self).__init__()
        self._filter = TrajectoryFilter(x0, object_size, object_size_error_ratio, decay=decay, coefficient=coefficient)
        self._maximum_heading_diff_allowed = math.pi * maximum_heading_diff_allowed_in_pi
        # histories
        self._zs = []
        self._xs = []
        self._covs = []
        self._xps = []
        self._ys = []
        self._Ks = []
        self._zs_candidates = []
        # reset each time step
        self._z_candidates = []

    @property
    def location(self):
        """ the current position of this PhaseSpaceObject instance

        An estimated current location based on this filter's prediction and a predicted position at time t

        returns (x, y) or None if no location history
        """
        if len(self._xs) == 0:
            return [self._filter.x[0], self._filter.x[3]]

        return [self._xs[-1][0], self._xs[-1][3]]

    @property
    def measurement(self):
        if len(self._zs) == 0:
            return None

        return [self._zs[-1][0], self._zs[-1][1]]

    @property
    def direction(self):
        """ the direction of this PhaseSpaceObject instance

        A direction ranges from -pi(-180) to pi(180),

        The difference between a direction and a heading is that 
        heading is the current direction, which could vary frequently,
        while direction is more stable because it is computed from the first to the last.

        return a float value (-pi, pi)  
        """
        if self.observed_travel_distance < max(*self._filter.object_size):
            return None

        return PhaseSpaceObject.radian_from_points(self._xs[0], self._xs[-1])

    @property
    def heading(self):
        """ the current direction of this PhaseSpaceObject instance

        A heading ranges from -pi(-180) to pi(180),

        return a float value (-pi, pi)  
        """
        if len(self._xs) < 2:
            return None

        return PhaseSpaceObject.radian_from_points(self._xs[-2], self._xs[-1])

    @staticmethod
    def radian_from_points(from_point, to_point):
        return math.atan2(to_point[1] - from_point[1], to_point[0] - from_point[0])

    @property
    def speed(self):
        """ pixels/frame

        returns a float value >= 0
        """
        movement = self.movement

        if movement is None:
            return None

        return math.sqrt(movement[0]**2 + movement[1]**2)

    @property
    def movement(self):
        """ the last movement of x, y, which is the speed in x and y
        """
        if len(self._xs) == 0:
            return None

        return [self._xs[-1][1], self._xs[-1][4]]

    @property
    def observed_travel_distance(self):
        """ the travel distance of observations
        """
        if len(self._zs) == 0:
            return -1

        # z contains None when no observed value is passed
        start, end = None, None
        for i in range(len(self._zs)):
            if start is None:
                start = self._zs[i]
            if end is None:
                end = self._zs[-1-1*i]
            if start is not None and end is not None:
                break

        if start is None or end is None:
            return -1

        return PhaseSpaceObject.distance_from_points(start, end)

    @staticmethod
    def distance_from_points(from_point, to_point):
        return math.sqrt((to_point[0] - from_point[0])**2 + (to_point[1] - from_point[1])**2)

    def update_location(self, z):
        """ update the current location by a predicted location and the given z(observed_location)
        """
        # predict
        self._filter.predict()
        if z is not None:
            self._filter.update(z)
        self._xs.append(self._filter.x)
        self._covs.append(self._filter.P)
        self._zs.append(z)
        self._xps.append(self._filter.x_prior)
        self._ys.append(self._filter.y)
        self._Ks.append(self._filter.K)
        # candidates
        self._zs_candidates.append(self._z_candidates)
        self._z_candidates = []

    def accept_measurement(self, z):
        """ check if a given measurement is acceptable
        """
        # calculate the next predicted position

        next_x = self._filter.F.dot(self._filter.x)

        # calculate residuals
        residual_x = abs(z[0] - next_x[0])
        residual_y = abs(z[1] - next_x[3])

        std_dev_x = math.sqrt(self._filter.P[0][0])
        std_dev_y = math.sqrt(self._filter.P[3][3])

        # check the change in the heading(this is often not reliable, so use with the distance following)
        current_direction = self.direction
        from_point = [self._filter.x[0], self._filter.x[3]]
        if current_direction is None:
            diff_heading = -1.0
        else:
            next_heading = PhaseSpaceObject.radian_from_points(from_point, z)
            diff_heading = abs(next_heading - current_direction)
            if diff_heading > math.pi:
                diff_heading -= math.pi

        # check distance
        distance = PhaseSpaceObject.distance_from_points(from_point, z)

        # accept if both residuals are within 99% range(3 * std_devs)
        # but reject when the heading difference and the moving distance are more than their thresholds
        accept = (residual_x < std_dev_x*3) and (residual_y < std_dev_y*3) and not (diff_heading > self._maximum_heading_diff_allowed and distance > max(*self._filter.object_size) * self._filter.object_size_error_ratio)

        self._z_candidates.append([z, next_x.T, [residual_x, residual_y], [std_dev_x, std_dev_y], accept, diff_heading, distance, max(*self._filter.object_size)])

        return accept

    @property
    def variance(self):
        """ the variances of locations """
        if len(self._covs) == 0:
            return None

        return [self._covs[-1][0][0], self._covs[-1][3][3]]

    @property
    def variance_speed(self):
        """ the variances of speeds """
        if len(self._covs) == 0:
            return None

        return [self._covs[-1][1][1], self._covs[-1][4][4]]

    @property
    def variance_accel(self):
        """ the variances of accelerations """
        if len(self._covs) == 0:
            return None

        return [self._covs[-1][2][2], self._covs[-1][5][5]]

    def update_object_size(self, new_object_size):
        self._filter.update_object_size(new_object_size)

    def history(self):

        buf = StringIO()
        for x, z, z_candidates, cov, x_prior, y, K in zip(self._xs, self._zs, self._zs_candidates, self._covs, self._xps, self._ys, self._Ks):
            buf.write(u'x_prior: \n{}\n'.format(x_prior))
            buf.write(u'z: \n{}\n'.format(z))
            buf.write(u'z_candidates: \n{}\n'.format(z_candidates))
            buf.write(u'y: \n{}\n'.format(y))
            buf.write(u'K: \n{}\n'.format(K))
            buf.write(u'x: \n{}\n'.format(x))
            buf.write(u'cov: \n{}\n'.format(cov))
            buf.write(u'=====================================\n')


        history = buf.getvalue()
        buf.close()

        return history
