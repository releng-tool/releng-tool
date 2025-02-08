# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io import path_exists
from tests import RelengToolTestCase
from tests.support import fetch_unittest_assets_dir


class TestUtilIoExists(RelengToolTestCase):
    def test_utilio_exists(self):
        assets_dir = fetch_unittest_assets_dir()

        self.assertTrue(path_exists(assets_dir))
        self.assertTrue(path_exists(assets_dir, 'copy-check-01'))
        self.assertTrue(path_exists(assets_dir, 'copy-check-01', 'test-file-a'))
