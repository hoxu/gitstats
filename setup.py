#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='gitstats',
        version='1.0',
        description='Git Statistic Utility',
        author='Raphael Freudiger',
        packages = find_packages(exclude=['build','dist']),
        package_data = {
                # Include *.gif or *.js files in the 'reporter' package:
                'gitstats.reporter': ['*.gif', '*.js'],
            },
        entry_points={
            'console_scripts': [
                'gitstats = gitstats:main',
            ],
        }
)
