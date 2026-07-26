# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsSbomFormat(TestDefaultEngineBase):
    def test_prjconfig_sbom_format_cfgcall_invalid_type(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    sbom_format=1,
)
''')

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_sbom_format_cfgcall_invalid_value(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    sbom_format='unknown',
)
''')

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_sbom_format_cfgcall_valid_list(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    sbom_format=[
        'csv',
        'json',
        'rdf-spdx',
    ],
)
''')

        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(len(opts.sbom_format), 3)
        self.assertIn('csv', opts.sbom_format)
        self.assertIn('json', opts.sbom_format)
        self.assertIn('rdf-spdx', opts.sbom_format)

    def test_prjconfig_sbom_format_cfgcall_valid_str(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    sbom_format='xml',
)
''')
        self.setprjcfg('sbom_format', 'xml')
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(len(opts.sbom_format), 1)
        self.assertIn('xml', opts.sbom_format)

    def test_prjconfig_sbom_format_global_invalid_type(self):
        self.setprjcfg('sbom_format', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_sbom_format_global_invalid_value(self):
        self.setprjcfg('sbom_format', 'unknown')

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_sbom_format_global_valid_list(self):
        self.setprjcfg('sbom_format', [
            'csv',
            'json',
            'rdf-spdx',
        ])
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(len(opts.sbom_format), 3)
        self.assertIn('csv', opts.sbom_format)
        self.assertIn('json', opts.sbom_format)
        self.assertIn('rdf-spdx', opts.sbom_format)

    def test_prjconfig_sbom_format_global_valid_str(self):
        self.setprjcfg('sbom_format', 'xml')
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(len(opts.sbom_format), 1)
        self.assertIn('xml', opts.sbom_format)
