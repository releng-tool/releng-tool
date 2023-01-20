# -*- coding: utf-8 -*-
# Copyright 2022-2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.util.io import path_exists
from tests.support import fetch_unittest_assets_dir
import unittest


class TestUtilIoExists(unittest.TestCase):
    def test_utilio_exists(self):
        assets_dir = fetch_unittest_assets_dir()

        self.assertTrue(path_exists(assets_dir))
        self.assertTrue(path_exists(assets_dir, 'copy-check-01'))
        self.assertTrue(path_exists(assets_dir, 'copy-check-01', 'test-file-a'))
