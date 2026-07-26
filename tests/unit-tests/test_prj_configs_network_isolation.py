# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsNetworkIsolation(TestDefaultEngineBase):
    def test_prjconfig_network_isolation_cfgcall_invalid(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    network_isolation=1,
)
''')

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_network_isolation_cfgcall_valid_false(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    network_isolation=False,
)
''')

        self.engine.run()

        opts = self.engine.opts
        self.assertFalse(opts.network_isolation)

    def test_prjconfig_network_isolation_cfgcall_valid_true(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    network_isolation=True,
)
''')

        self.engine.run()

        opts = self.engine.opts
        self.assertTrue(opts.network_isolation)

    def test_prjconfig_network_isolation_global_invalid(self):
        self.setprjcfg('network_isolation', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_network_isolation_global_valid_false(self):
        self.setprjcfg('network_isolation', value=False)
        self.engine.run()

        opts = self.engine.opts
        self.assertFalse(opts.network_isolation)

    def test_prjconfig_network_isolation_global_valid_true(self):
        self.setprjcfg('network_isolation', value=True)
        self.engine.run()

        opts = self.engine.opts
        self.assertTrue(opts.network_isolation)
