# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util import global_define
from releng_tool.util import nullish_coalescing
from tests import RelengToolTestCase


class TestUtilCommon(RelengToolTestCase):
    def test_util_global_define(self):
        # cleanup
        if 'RELENG_TOOL_TEST_GD' in globals():
            del globals()['RELENG_TOOL_TEST_GD']

        # using provided value
        value = global_define('RELENG_TOOL_TEST_GD', default='a')
        self.assertEqual(value, 'a')
        self.assertEqual(globals()['RELENG_TOOL_TEST_GD'], 'a')
        self.assertEqual(
            RELENG_TOOL_TEST_GD, 'a')  # noqa: F821  pylint: disable=E0602

        # already configured
        value = global_define('RELENG_TOOL_TEST_GD', default='b')
        self.assertEqual(value, 'a')
        self.assertEqual(
            RELENG_TOOL_TEST_GD, 'a')  # noqa: F821  pylint: disable=E0602

        # cleanup
        del globals()['RELENG_TOOL_TEST_GD']

        # handle no default
        value = global_define('RELENG_TOOL_TEST_GD')
        self.assertIsNone(value)
        self.assertIsNone(
            RELENG_TOOL_TEST_GD)  # noqa: F821  pylint: disable=E0602

        # already configured
        value = global_define('RELENG_TOOL_TEST_GD', default='c')
        self.assertIsNone(value)
        self.assertIsNone(
            RELENG_TOOL_TEST_GD)  # noqa: F821  pylint: disable=E0602

        # cleanup
        del globals()['RELENG_TOOL_TEST_GD']

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
            dict(),  # noqa: C408
            list(),  # noqa: C408
            set(),
        ]
        for check in checks:
            value = nullish_coalescing(check, 'err')
            self.assertEqual(value, check)
