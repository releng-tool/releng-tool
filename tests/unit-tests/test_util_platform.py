# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.util.platform import platform_exit
from tests import redirect_stderr
import unittest


class TestUtilPlatform(unittest.TestCase):
    def test_util_platform_error(self):
        with self.assertRaises(SystemExit) as cm:
            platform_exit(code=123)

        self.assertEqual(cm.exception.code, 123)

    def test_util_platform_message_no_code(self):
        with redirect_stderr() as stream:
            with self.assertRaises(SystemExit) as cm:
                platform_exit('my message')

        self.assertIn('my message', stream.getvalue())
        self.assertEqual(cm.exception.code, 1)

    def test_util_platform_message_with_code(self):
        with redirect_stderr() as stream:
            with self.assertRaises(SystemExit) as cm:
                platform_exit('my message', 456)

        self.assertIn('my message', stream.getvalue())
        self.assertEqual(cm.exception.code, 456)

    def test_util_platform_success(self):
        with self.assertRaises(SystemExit) as cm:
            platform_exit()

        self.assertEqual(cm.exception.code, 0)
