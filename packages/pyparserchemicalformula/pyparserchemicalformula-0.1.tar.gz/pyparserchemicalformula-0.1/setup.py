#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of MahewinHubStar.
# https://github.com/hobbestigrou/MahewinHubStar

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2015, Hobbestigrou <hobbestigrou@erakis.eu>

from setuptools import setup, find_packages

setup(
    name='pyparserchemicalformula',
    version='0.1',
    description='To parse chemical formula.',
    long_description='''
To parse chemical formula with python.
''',
    keywords='parser, chemical',
    author='Hobbestigrou',
    author_email='hobbestigrou@erakis.eu',
    url='https://github.com/hobbestigrou/pyparserchemicalformula',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=False,
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
        ],
    },
)
