# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util import nullish_coalescing
from tests import RelengToolTestCase


class TestUtilCommon(RelengToolTestCase):
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
