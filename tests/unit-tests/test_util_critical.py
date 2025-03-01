# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.critical import raise_for_critical
from tests import RelengToolTestCase


class TestUtilCritical(RelengToolTestCase):
    def test_util_critical_no_raise_no_flag(self):
        raise_for_critical(flag=False)

    def test_util_critical_no_raise_on_none(self):
        raise_for_critical(None)

    def test_util_critical_raise_no_arg(self):
        with self.assertRaises(SystemExit):
            raise_for_critical()

    def test_util_critical_raise_on_flag(self):
        with self.assertRaises(SystemExit):
            raise_for_critical(flag=True)

    def test_util_critical_raise_on_result(self):
        with self.assertRaises(SystemExit):
            raise_for_critical('error-state')
