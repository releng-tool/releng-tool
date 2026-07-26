# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase
from unittest.mock import MagicMock
from unittest.mock import patch


class TestPrjConfigsVsDevCmd(TestDefaultEngineBase):
    def test_prjconfig_vsdevcmd_global_invalid(self):
        self.setprjcfg('vsdevcmd', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    @patch('releng_tool.engine.vsdevcmd_initialize', new=MagicMock)
    def test_prjconfig_vsdevcmd_global_valid_bool(self):
        self.setprjcfg('vsdevcmd', value=True)
        self.engine.run()

        opts = self.engine.opts
        self.assertTrue(opts.vsdevcmd)

    @patch('releng_tool.engine.vsdevcmd_initialize', new=MagicMock)
    def test_prjconfig_vsdevcmd_global_valid_str(self):
        self.setprjcfg('vsdevcmd', '[17.0,18.0)')
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.vsdevcmd, '[17.0,18.0)')
