#!/usr/bin/env python

from setuptools import setup
import purses
setup(
    name='purses',
    version='0.0.1',
    packages=[
        'purses',
    ],
    author='pgdr@equinor.com',
    author_email='pgdr@equinor.com',
    description="Purses, a Pandas Curses",
    tests_require=[
        'pandas',
    ],
    install_requires=['pandas'],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'purses = purses:main'
        ]
    },
)
