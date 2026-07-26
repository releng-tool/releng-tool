# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsLicenseHeader(TestDefaultEngineBase):
    def test_prjconfig_license_header_cfgcall_invalid(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    license_header=1,
)
''')

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_license_header_cfgcall_valid(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    license_header='This is a header.',
)
''')

        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.license_header, 'This is a header.')

    def test_prjconfig_license_header_global_invalid(self):
        self.setprjcfg('license_header', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_license_header_global_valid(self):
        self.setprjcfg('license_header', 'This is a header.')
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.license_header, 'This is a header.')
