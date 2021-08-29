#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from distutils.command.clean import clean
from distutils import dir_util
from setuptools import find_packages
from setuptools import setup
import os

def read(name):
    return open(os.path.join(os.path.dirname(__file__), name)).read()

# remove extra resources not removed by the default clean operation
class ExtendedClean(clean):
    def run(self):
        clean.run(self)

        if not self.all:
            return

        extras = [
            'dist',
            'releng_tool.egg-info',
        ]
        for extra in extras:
            if os.path.exists(extra):
                dir_util.remove_tree(extra, dry_run=self.dry_run)

setup(
    author='releng-tool',
    author_email='releng@releng.io',
    classifiers=[
        'Development Status :: 4 - Beta',
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
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
    ],
    cmdclass={
        'clean': ExtendedClean,
    },
    description='release engineering utility tool',
    entry_points={
        'console_scripts': [
            'releng-tool = releng_tool.__main__:main',
        ],
    },
    extras_require={
        'statistics': [
            'matplotlib',
        ],
    },
    license='BSD-2-Clause',
    long_description=read('README.rst'),
    name='releng-tool',
    packages=find_packages(exclude=["tests*"]),
    platforms='any',
    test_suite='tests',
    url='https://releng.io',
    version='0.9.0.dev0',
    zip_safe=False,
)
