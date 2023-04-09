# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.util.io import ls
from tests import prepare_workdir
from tests import redirect_stdout
import os
import unittest


class TestUtilIoLs(unittest.TestCase):
    def test_utilio_ls_invalid_directory(self):
        with redirect_stdout() as stream:
            listed = ls(os.path.realpath(__file__))

        self.assertFalse(listed)
        self.assertEqual(stream.getvalue(), '')

    def test_utilio_ls_missing_directory(self):
        with redirect_stdout() as stream:
            listed = ls('missing-directory')

        self.assertFalse(listed)
        self.assertEqual(stream.getvalue(), '')

    def test_utilio_ls_valid_directory_contents(self):
        base_dir = os.path.dirname(os.path.realpath(__file__))

        with redirect_stdout() as stream:
            listed = ls(base_dir)

        self.assertTrue(listed)

        entries = stream.getvalue().split('\n')
        self.assertTrue('assets/' in entries)
        self.assertTrue('__init__.py' in entries)
        self.assertTrue('test_util_io_cat.py' in entries)

    def test_utilio_ls_valid_directory_empty(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as empty_dir:
                listed = ls(empty_dir)

        self.assertTrue(listed)
        self.assertEqual(stream.getvalue(), '')
