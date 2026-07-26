# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsVsDevCmdProducts(TestDefaultEngineBase):
    def test_prjconfig_vsdevcmd_products_global_invalid(self):
        self.setprjcfg('vsdevcmd_products', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_vsdevcmd_products_global_valid(self):
        self.setprjcfg(
            'vsdevcmd_products',
            'Microsoft.VisualStudio.Product.BuildTools',
        )
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(
            opts.vsdevcmd_products,
            'Microsoft.VisualStudio.Product.BuildTools',
        )
