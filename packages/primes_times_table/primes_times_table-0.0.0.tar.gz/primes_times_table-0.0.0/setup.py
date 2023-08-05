#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='primes_times_table',
    version='0.0.0',
    author='Jacob Powers',
    author_email='powersjcb@gmail.com',
    url='https://github.com/powersjcb/primes_times_table',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'genprimes = primes_times_table:main'
        ],
    },
)