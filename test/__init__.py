#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from contextlib import contextmanager
from releng.util.io import generateTempDir as tempDir
from difflib import unified_diff
from io import open
import os

"""
base output directory for unit tests using a file system
"""
TEST_OUTPUT_DIR = 'output'

class RelengTestUtil:
    """
    releng-tool test utility class

    This class is used to hold a series of utility methods, etc. to assist in
    testing.
    """

    @staticmethod
    def compare(first, second):
        """
        compare the contents of two files

        This utility method is used to compare the contents of two files. Both
        file's contents will be read and checked for any differences. If both
        files have the same contents, `None` will be returned; otherwise a
        string containing a unified diff string will be returned.

        Args:
            first: the first file
            second: the second file

        Returns:
            `None` if matching; otherwise a unified diff string
        """
        def strip_lines(lines):
            return [line.strip() + '\n' for line in lines]

        try:
            with open(first, mode='r', encoding='utf_8') as file:
                content1 = strip_lines(file.readlines())
        except IOError:
            return 'failed to load first file: ' + first

        try:
            with open(second, mode='r', encoding='utf_8') as file:
                content2 = strip_lines(file.readlines())
        except IOError:
            return 'failed to load second file: ' + second

        diff = unified_diff(content1, content2,
            fromfile=first, tofile=second, lineterm='\n')
        diff_content = ''.join(list(diff))
        if diff_content:
            return 'unexpected file differences\n{}'.format(diff_content)

        return None

    @staticmethod
    @contextmanager
    def prepareWorkdir():
        """
        prepare a working directory for a test

        This utility method is used to provide a test a directory to store
        output files. This method will ensure the container directory is emptied
        before returning.

        Returns:
            the container directory
        """

        base_dir = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(base_dir, TEST_OUTPUT_DIR)

        with tempDir(output_dir) as work_dir:
            yield work_dir
