# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io_path import releng_register_python_path
from releng_tool.util.io_temp_dir import temp_dir
from tests import RelengToolTestCase
import sys


class TestUtilIoPathRegisterPythonPath(RelengToolTestCase):
    def test_utilio_path_register_python_path_invalid_crtiical(self):
        with self.assertRaises(SystemExit):
            releng_register_python_path('RELENG_TOOL_TEST_BADPATH')

    def test_utilio_path_register_python_path_invalid_noncritical(self):
        rv = releng_register_python_path(
            'RELENG_TOOL_TEST_BADPATH', critical=False)
        self.assertFalse(rv)

    def test_utilio_path_register_python_path_prepend(self):
        with temp_dir() as tmp_dir:
            rv = releng_register_python_path(tmp_dir, prepend=True)
            self.assertTrue(rv)

            # path is first
            self.assertEqual(tmp_dir, sys.path[0])

    def test_utilio_path_register_python_path_single(self):
        with temp_dir() as tmp_dir:
            rv = releng_register_python_path(tmp_dir)
            self.assertTrue(rv)

            # register a second time
            rv = releng_register_python_path(tmp_dir)
            self.assertTrue(rv)

            # should still only have one
            self.assertEqual(sys.path.count(tmp_dir), 1)

    def test_utilio_path_register_python_path_valid(self):
        with temp_dir() as tmp_dir:
            rv = releng_register_python_path(tmp_dir)
            self.assertTrue(rv)
            self.assertIn(tmp_dir, sys.path)
