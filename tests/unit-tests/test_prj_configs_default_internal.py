# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsDefaultInternal(TestDefaultEngineBase):
    def test_prjconfig_default_internal_global_invalid(self):
        self.setprjcfg('default_internal', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_default_internal_global_valid_false(self):
        self.setprjcfg('default_internal', value=False)
        self.engine.run()

        opts = self.engine.opts
        self.assertFalse(opts.default_internal_pkgs)

    def test_prjconfig_default_internal_global_valid_true(self):
        self.setprjcfg('default_internal', value=True)
        self.engine.run()

        opts = self.engine.opts
        self.assertTrue(opts.default_internal_pkgs)
