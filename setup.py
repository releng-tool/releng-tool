#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

from setuptools import find_packages
from setuptools import setup
import os

def read(name):
    return open(os.path.join(os.path.dirname(__file__), name)).read()

setup(
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
    ],
    description='release engineering utility tool',
    entry_points={
        'console_scripts': [
            'releng-tool = releng.__main__:main',
        ],
    },
    install_requires=[
        "enum34; python_version == '2.7'"
    ],
    license='BSD-2-Clause',
    long_description=read('README.rst'),
    name='releng-tool',
    packages=find_packages(exclude=["test*"]),
    platforms='any',
    test_suite='test',
    url='https://github.com/releng-tool/releng-tool',
    version='0.1.0.dev6',
    zip_safe=False,
)
