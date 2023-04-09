# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool import __version__ as releng_version
from releng_tool.support import require_version
import unittest


class TestSupport(unittest.TestCase):
    def test_support_require_version(self):
        # existing version should report has valid
        result = require_version(releng_version)
        self.assertTrue(result)

        # an old version should report has valid
        result = require_version('0.0')
        self.assertTrue(result)

        # fail version check on a future version which does not exist
        result = require_version('999999', critical=False)
        self.assertFalse(result)

        # fail version check on a future version which does not exist (critical)
        with self.assertRaises(SystemExit):
            require_version('999999')
