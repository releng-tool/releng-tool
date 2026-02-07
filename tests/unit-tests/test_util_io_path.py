# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_path import path_input
from releng_tool.util.io_path import releng_register_path
from releng_tool.util.io_temp_dir import temp_dir
from tests import RelengToolTestCase
import os
import sys


class TestUtilIoPath(RelengToolTestCase):
    def test_utilio_path_check(self):
        self.assertEqual(path_input(__file__), Path(__file__))

    def test_utilio_path_expanded(self):
        test_file = Path(__file__)
        base_dir = test_file.parent
        os.environ['FILE_NAME'] = test_file.name
        test_file_str = f'{base_dir}/${{FILE_NAME}}'
        self.assertEqual(path_input(test_file_str), test_file)

    def test_utilio_path_register_invalid_crtiical(self):
        with self.assertRaises(SystemExit):
            releng_register_path('RELENG_TOOL_TEST_BADPATH')

    def test_utilio_path_register_invalid_noncritical(self):
        rv = releng_register_path('RELENG_TOOL_TEST_BADPATH', critical=False)
        self.assertFalse(rv)

    def test_utilio_path_register_single(self):
        with temp_dir() as tmp_dir:
            rv = releng_register_path(tmp_dir)
            self.assertTrue(rv)

            # register a second time
            rv = releng_register_path(tmp_dir)
            self.assertTrue(rv)

            # should still only have one
            self.assertEqual(sys.path.count(tmp_dir), 1)

    def test_utilio_path_register_valid(self):
        with temp_dir() as tmp_dir:
            rv = releng_register_path(tmp_dir)
            self.assertTrue(rv)
            self.assertIn(tmp_dir, sys.path)
