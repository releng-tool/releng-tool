# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests import setprjcfg
from tests.support.default_engine_test import TestDefaultEngineBase
from unittest.mock import MagicMock
from unittest.mock import patch


class TestPrjConfigsVsDevCmd(TestDefaultEngineBase):
    def test_prjconfig_vsdevcmd_invalid(self):
        setprjcfg(self.engine, 'vsdevcmd', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    @patch('releng_tool.engine.vsdevcmd_initialize', new=MagicMock)
    def test_prjconfig_vsdevcmd_valid_bool(self):
        setprjcfg(self.engine, 'vsdevcmd', value=True)
        self.engine.run()

        opts = self.engine.opts
        self.assertTrue(opts.vsdevcmd)

    @patch('releng_tool.engine.vsdevcmd_initialize', new=MagicMock)
    def test_prjconfig_vsdevcmd_valid_str(self):
        setprjcfg(self.engine, 'vsdevcmd', '[17.0,18.0)')
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.vsdevcmd, '[17.0,18.0)')
