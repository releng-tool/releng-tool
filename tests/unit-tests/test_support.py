# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool import __version__ as releng_version
from releng_tool.support import require_version
from unittest.mock import patch
from tests import RelengToolTestCase


class TestSupport(RelengToolTestCase):
    def test_support_require_version_current(self):
        # existing version should report has valid
        result = require_version(minver=releng_version)
        self.assertTrue(result)

    def test_support_require_version_older_case01(self):
        # an old version should report has valid
        result = require_version('0.0')
        self.assertTrue(result)

    @patch('releng_tool.support.releng_version', new='2.0')
    def test_support_require_version_older_case02(self):
        result = require_version('2.0')
        self.assertTrue(result)

    @patch('releng_tool.support.releng_version', new='1.1234.5')
    def test_support_require_version_older_case03(self):
        result = require_version('1.1234.5')
        self.assertTrue(result)

    @patch('releng_tool.support.releng_version', new='1.1234.5')
    def test_support_require_version_older_case04(self):
        result = require_version('1.5')
        self.assertTrue(result)

    @patch('releng_tool.support.releng_version', new='1.1234.5')
    def test_support_require_version_older_case05(self):
        result = require_version('1.1233.6')
        self.assertTrue(result)

    @patch('releng_tool.support.releng_version', new='1.0.0.0.0.2')
    def test_support_require_version_older_case06(self):
        result = require_version('1', critical=False)
        self.assertTrue(result)

    def test_support_require_version_future_case01(self):
        # fail version check on a future version which does not exist
        result = require_version('999999', critical=False)
        self.assertFalse(result)

    @patch('releng_tool.support.releng_version', new='1.0.0')
    def test_support_require_version_future_case02(self):
        # fail version check on a future version which does not exist
        result = require_version('1.0.1', critical=False)
        self.assertFalse(result)

    @patch('releng_tool.support.releng_version', new='2.9')
    def test_support_require_version_future_case03(self):
        # fail version check on a future version which does not exist
        result = require_version('2.10', critical=False)
        self.assertFalse(result)

    @patch('releng_tool.support.releng_version', new='12.34.56')
    def test_support_require_version_future_case04(self):
        # fail version check on a future version which does not exist
        result = require_version('13.34.56', critical=False)
        self.assertFalse(result)

    @patch('releng_tool.support.releng_version', new='1.0')
    def test_support_require_version_future_case05(self):
        result = require_version('1.0.0.0.1', critical=False)
        self.assertFalse(result)

    def test_support_require_version_future_critical(self):
        # fail version check on a future version which does not exist (critical)
        with self.assertRaises(SystemExit):
            require_version('999999')

    def test_support_require_version_max_older_case01(self):
        # ensure max older version triggers a failure
        result = require_version(maxver='0.0', critical=False)
        self.assertFalse(result)

    @patch('releng_tool.support.releng_version', new='2.10')
    def test_support_require_version_max_older_case02(self):
        result = require_version(maxver='2.9.1', critical=False)
        self.assertFalse(result)

    @patch('releng_tool.support.releng_version', new='12.34.56')
    def test_support_require_version_max_older_case03(self):
        result = require_version(maxver='12.34.55', critical=False)
        self.assertFalse(result)

    @patch('releng_tool.support.releng_version', new='3.19')
    def test_support_require_version_max_older_case04(self):
        result = require_version(maxver='3.20', critical=False)
        self.assertTrue(result)

    @patch('releng_tool.support.releng_version', new='12.34.56')
    def test_support_require_version_max_older_case05(self):
        result = require_version(maxver='12.34.57', critical=False)
        self.assertTrue(result)

    def test_support_require_version_invalid_value(self):
        with self.assertRaises(SystemExit):
            require_version('some-odd-value')
