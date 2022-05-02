#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2022 releng-tool

from distutils.command.clean import clean
from distutils import dir_util
from setuptools import find_packages
from setuptools import setup
import os

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
    cmdclass={
        'clean': ExtendedClean,
    },
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
    packages=find_packages(exclude=["tests*"]),
    test_suite='tests',
    version='0.12.0',
    zip_safe=False,
)
