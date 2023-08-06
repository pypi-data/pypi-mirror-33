from setuptools import setup, find_packages

setup(
    name='trajectorypy',
    version='1.0.0-a3',
    description='trajectorypy is a library to track a trajectory',
    url='https://github.com/ggsato/trajectorypy',
    author='Takenori Sato',
    author_email='takenori.sato@gmail.com',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
	],
	# What does your project relate to?
	keywords='object tracking, kalman filtering, computer vision',
    packages=find_packages(),
    install_requires=[
        'filterpy==1.4.0'
    ],
    python_requires='>=2.7',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
