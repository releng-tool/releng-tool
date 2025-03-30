# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_exists import path_exists
from tests import RelengToolTestCase
from tests.support import fetch_unittest_assets_dir


class TestUtilIoExists(RelengToolTestCase):
    def test_utilio_exists(self):
        assets_dir = fetch_unittest_assets_dir()

        self.assertTrue(path_exists(assets_dir))
        self.assertTrue(path_exists(assets_dir, b'__init__.py'))
        self.assertTrue(path_exists(assets_dir, 'copy-check-01'))
        self.assertTrue(path_exists(assets_dir, 'copy-check-01', 'test-file-a'))
        self.assertTrue(path_exists(assets_dir, Path('copy-check-02')))
        self.assertFalse(path_exists('this-file-does-not-exist'))
