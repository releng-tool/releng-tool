# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsDefaultDevIgnoreCache(TestDefaultEngineBase):
    def test_prjconfig_default_dev_ignore_cache_invalid(self):
        self.setprjcfg('default_devmode_ignore_cache', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_default_internal_valid_false(self):
        self.setprjcfg('default_devmode_ignore_cache', value=False)
        self.engine.run()

        opts = self.engine.opts
        self.assertFalse(opts.default_dev_ignore_cache)

    def test_prjconfig_default_internal_valid_true(self):
        self.setprjcfg('default_devmode_ignore_cache', value=True)
        self.engine.run()

        opts = self.engine.opts
        self.assertTrue(opts.default_dev_ignore_cache)
