# -*- coding: utf-8 -*-
# Copyright 2021-2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.util import nullish_coalescing
import unittest


class TestUtilCommon(unittest.TestCase):
    def test_util_nullish_coalescing(self):
        # using provided value
        value = nullish_coalescing('test', None)
        self.assertEqual(value, 'test')

        value = nullish_coalescing('test2', 'test3')
        self.assertEqual(value, 'test2')

        # using default
        value = nullish_coalescing(None, 'test4')
        self.assertEqual(value, 'test4')

        # sanity check against False evaluated types
        checks = [
            '',
            0,
            dict(),
            list(),
            set(),
        ]
        for check in checks:
            value = nullish_coalescing(check, 'err')
            self.assertEqual(value, check)
