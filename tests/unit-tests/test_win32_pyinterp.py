# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from releng_tool.util.win32 import find_win32_python_interpreter
import os
import sys
import unittest


class TestWin32PyInterp(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        if sys.platform != 'win32':
            raise unittest.SkipTest('only win32')

    def test_win32_pyinterp_default(self):
        interp = find_win32_python_interpreter('python')
        self.assertIsNotNone(interp)
        self.assertTrue(os.path.isfile(interp))

    def test_win32_pyinterp_missing(self):
        interp = find_win32_python_interpreter('')
        self.assertIsNone(interp)

    def test_win32_pyinterp_nonexistent(self):
        interp = find_win32_python_interpreter('python1.2.3')
        self.assertIsNone(interp)

    def test_win32_pyinterp_py039(self):
        if sys.version_info[:2] != (3, 9):
            raise self.skipTest('only run in py0309')

        interp = find_win32_python_interpreter('python3.9')
        self.assertIsNotNone(interp)
        self.assertTrue(os.path.isfile(interp))

    def test_win32_pyinterp_py0310(self):
        if sys.version_info[:2] != (3, 10):
            raise self.skipTest('only run in py0310')

        interp = find_win32_python_interpreter('python3.10')
        self.assertIsNotNone(interp)
        self.assertTrue(os.path.isfile(interp))

    def test_win32_pyinterp_py0311(self):
        if sys.version_info[:2] != (3, 11):
            raise self.skipTest('only run in py0311')

        interp = find_win32_python_interpreter('python3.11')
        self.assertIsNotNone(interp)
        self.assertTrue(os.path.isfile(interp))

    def test_win32_pyinterp_py0312(self):
        if sys.version_info[:2] != (3, 12):
            raise self.skipTest('only run in py0312')

        interp = find_win32_python_interpreter('python3.12')
        self.assertIsNotNone(interp)
        self.assertTrue(os.path.isfile(interp))

    def test_win32_pyinterp_py0313(self):
        if sys.version_info[:2] != (3, 13):
            raise self.skipTest('only run in py0313')

        interp = find_win32_python_interpreter('python3.13')
        self.assertIsNotNone(interp)
        self.assertTrue(os.path.isfile(interp))

    def test_win32_pyinterp_py0314(self):
        if sys.version_info[:2] != (3, 14):
            raise self.skipTest('only run in py0314')

        interp = find_win32_python_interpreter('python3.14')
        self.assertIsNotNone(interp)
        self.assertTrue(os.path.isfile(interp))
