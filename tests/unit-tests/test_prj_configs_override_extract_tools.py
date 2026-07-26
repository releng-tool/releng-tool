# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsOverrideExtractTools(TestDefaultEngineBase):
    def test_prjconfig_override_extract_tools_invalid(self):
        self.setprjcfg('override_extract_tools', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_override_extract_tools_valid(self):
        self.setprjcfg('override_extract_tools', {
            'zip': '/opt/my-custom-unzip {file} {dir}',
        })
        self.engine.run()

        opts = self.engine.opts
        self.assertIsNotNone(opts.extract_override)
        self.assertIn('zip', opts.extract_override)
        self.assertEqual(
            opts.extract_override['zip'],
            '/opt/my-custom-unzip {file} {dir}',
        )
