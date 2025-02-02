# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
import os
import sys


class TestMisc(RelengToolTestCase):
    def test_misc_sanity_check_envwrap(self):
        self.assertNotIn('RELENG_TOOL_TEST_ENVWRAP_CHECK', os.environ)

        with self.env_wrap():
            os.environ['RELENG_TOOL_TEST_ENVWRAP_CHECK'] = '1'

            self.assertIn('RELENG_TOOL_TEST_ENVWRAP_CHECK', os.environ)

        self.assertNotIn('RELENG_TOOL_TEST_ENVWRAP_CHECK', os.environ)

    def test_misc_sanity_check_syspath_wrap(self):
        self.assertNotIn('RELENG_TOOL_TEST_SYSPATH_CHECK', sys.path)

        with self.syspath_wrap():
            sys.path.insert(0, 'RELENG_TOOL_TEST_SYSPATH_CHECK')

            self.assertIn('RELENG_TOOL_TEST_SYSPATH_CHECK', sys.path)

        self.assertNotIn('RELENG_TOOL_TEST_SYSPATH_CHECK', sys.path)
