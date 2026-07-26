# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsExtraLicenseExceptions(TestDefaultEngineBase):
    def test_prjconfig_extra_license_exceptions_global_invalid(self):
        self.setprjcfg('extra_license_exceptions', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_extra_license_exceptions_global_valid(self):
        self.setprjcfg('extra_license_exceptions', value={
            'My-Exception-ID': 'Exception Name',
        })
        self.engine.run()

        opts = self.engine.opts
        self.assertIn('My-Exception-ID', opts.spdx['exceptions'])
        self.assertEqual(
            opts.spdx['exceptions']['My-Exception-ID']['name'],
            'Exception Name',
        )
