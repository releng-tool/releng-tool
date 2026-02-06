# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.platform import platform_exit
from tests import RelengToolTestCase
from tests import redirect_stdout
import os


class TestUtilPlatform(RelengToolTestCase):
    def test_util_platform_error(self):
        with self.assertRaises(SystemExit) as cm:
            platform_exit(code=123)

        self.assertEqual(cm.exception.code, 123)

    def test_util_platform_message_expanded(self):
        os.environ['MSG_TYPE'] = 'special'

        with redirect_stdout() as stream:
            with self.assertRaises(SystemExit):
                platform_exit('my $MSG_TYPE message')

        self.assertIn('my special message', stream.getvalue())

    def test_util_platform_message_no_code(self):
        with redirect_stdout() as stream:
            with self.assertRaises(SystemExit) as cm:
                platform_exit('my message')

        self.assertIn('my message', stream.getvalue())
        self.assertEqual(cm.exception.code, 1)

    def test_util_platform_message_with_code(self):
        with redirect_stdout() as stream:
            with self.assertRaises(SystemExit) as cm:
                platform_exit('my message', 456)

        self.assertIn('my message', stream.getvalue())
        self.assertEqual(cm.exception.code, 456)

    def test_util_platform_success(self):
        with self.assertRaises(SystemExit) as cm:
            platform_exit()

        self.assertEqual(cm.exception.code, 0)
