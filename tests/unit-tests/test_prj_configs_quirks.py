# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsQuirks(TestDefaultEngineBase):
    def test_prjconfig_quirks_cfgcall_invalid(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    quirks=1,
)
''')

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_quirks_cfgcall_valid_list(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    quirks=[
        'releng.quirk1',
        'releng.quirk2',
        'releng.quirk4',
    ],
)
''')

        self.engine.run()

        opts = self.engine.opts
        self.assertIn('releng.quirk1', opts.quirks)
        self.assertIn('releng.quirk2', opts.quirks)
        self.assertIn('releng.quirk4', opts.quirks)

    def test_prjconfig_quirks_cfgcall_valid_str(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    quirks='releng.quirk3',
)
''')

        self.engine.run()

        opts = self.engine.opts
        self.assertIn('releng.quirk3', opts.quirks)

    def test_prjconfig_quirks_global_invalid(self):
        self.setprjcfg('quirks', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_quirks_global_valid_list(self):
        self.setprjcfg('quirks', [
            'releng.quirk1',
            'releng.quirk2',
            'releng.quirk4',
        ])
        self.engine.run()

        opts = self.engine.opts
        self.assertIn('releng.quirk1', opts.quirks)
        self.assertIn('releng.quirk2', opts.quirks)
        self.assertIn('releng.quirk4', opts.quirks)

    def test_prjconfig_quirks_global_valid_str(self):
        self.setprjcfg('quirks', 'releng.quirk3')
        self.engine.run()

        opts = self.engine.opts
        self.assertIn('releng.quirk3', opts.quirks)
