# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_path import path_input
from tests import RelengToolTestCase
import os


class TestUtilIoPath(RelengToolTestCase):
    def test_utilio_path_check(self):
        self.assertEqual(path_input(__file__), Path(__file__))

    def test_utilio_path_expanded(self):
        test_file = Path(__file__)
        base_dir = test_file.parent
        os.environ['FILE_NAME'] = test_file.name
        test_file_str = f'{base_dir}/${{FILE_NAME}}'
        self.assertEqual(path_input(test_file_str), test_file)
