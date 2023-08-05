#!/usr/bin/env python3
from setuptools import setup
from docker_ascii_map import __version__

setup(
    name='docker-ascii-map',
    version=__version__,
    packages=['docker_ascii_map'],
    package_dir={'docker_ascii_map': 'docker_ascii_map'},
    scripts=['docker_ascii_map/docker-ascii-map'],
    test_suite='tests',
    setup_requires=['pytest-runner'],
    install_requires=['docker-py >= 1.10.0', 'termcolor >= 1.1.0'],
    tests_require=['pytest'],
    url='https://gitlab.com/alcibiade/docker-ascii-map',
    license='MIT',
    author='Yannick Kirschhoffer',
    author_email='alcibiade@alcibiade.org',
    description='A set of python scripts displaying the local docker containers structure and status on an ascii map.',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
