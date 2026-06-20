# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests import setprjcfg
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsNetworkIsolation(TestDefaultEngineBase):
    def test_prjconfig_network_isolation_invalid(self):
        setprjcfg(self.engine, 'network_isolation', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_network_isolation_valid(self):
        setprjcfg(self.engine, 'network_isolation', value=True)
        self.engine.run()

        opts = self.engine.opts
        self.assertTrue(opts.network_isolation)
