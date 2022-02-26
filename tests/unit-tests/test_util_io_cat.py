# -*- coding: utf-8 -*-
# Copyright 2022 releng-tool

from releng_tool.util.io import cat
from tests import prepare_workdir
from tests import redirect_stdout
import os
import unittest


class TestUtilIoCat(unittest.TestCase):
    def test_utilio_cat_invalid_file(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as test_dir:
                output = cat(test_dir)

        self.assertFalse(output)
        self.assertEqual(stream.getvalue(), '')

    def test_utilio_cat_missing_file(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as test_dir:
                test_file = os.path.join(test_dir, 'missing-file')

                output = cat(test_file)

        self.assertFalse(output)
        self.assertEqual(stream.getvalue(), '')

    def test_utilio_cat_valid_contents_multiple(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as test_dir:
                test_file1 = os.path.join(test_dir, 'test1')
                with open(test_file1, 'w') as f:
                    f.write('1')

                test_file2 = os.path.join(test_dir, 'test2')
                with open(test_file2, 'w') as f:
                    f.write('2')

                test_file3 = os.path.join(test_dir, 'test3')
                with open(test_file3, 'w') as f:
                    f.write('3')

                output = cat(test_file1, test_file2, test_file3)

        self.assertTrue(output)
        self.assertEqual(stream.getvalue(), '123')

    def test_utilio_cat_valid_contents_single(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as test_dir:
                test_file = os.path.join(test_dir, 'test')

                with open(test_file, 'w') as f:
                    f.write('this is a test')

                output = cat(test_file)

        self.assertTrue(output)
        self.assertEqual(stream.getvalue(), 'this is a test')

    def test_utilio_cat_valid_empty(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as test_dir:
                test_file = os.path.join(test_dir, 'test')

                with open(test_file, 'w'):
                    pass  # empty

                output = cat(test_file)

        self.assertTrue(output)
        self.assertEqual(stream.getvalue(), '')
