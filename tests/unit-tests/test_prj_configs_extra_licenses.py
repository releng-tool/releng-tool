# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsExtraLicenses(TestDefaultEngineBase):
    def test_prjconfig_extra_licenses_invalid(self):
        self.setprjcfg('extra_licenses', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_extra_licenses_valid(self):
        self.setprjcfg('extra_licenses', value={
            'My-License-ID': 'License Name',
        })
        self.engine.run()

        opts = self.engine.opts
        self.assertIn('My-License-ID', opts.spdx['licenses'])
        self.assertEqual(
            opts.spdx['licenses']['My-License-ID']['name'], 'License Name')
