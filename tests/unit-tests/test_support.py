# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool import __version__ as releng_version
from releng_tool.support import require_version
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

    def test_support_require_version_future_case01(self):
        # fail version check on a future version which does not exist
        result = require_version('999999', critical=False)
        self.assertFalse(result)

    def test_support_require_version_future_critical(self):
        # fail version check on a future version which does not exist (critical)
        with self.assertRaises(SystemExit):
            require_version('999999')

    def test_support_require_version_max_older(self):
        # ensure max older version triggers a failure
        result = require_version(maxver='0.0', critical=False)
        self.assertFalse(result)
