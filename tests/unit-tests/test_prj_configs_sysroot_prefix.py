# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsSysrootPrefix(TestDefaultEngineBase):
    def test_prjconfig_sysroot_prefix_cfgcall_invalid(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    sysroot_prefix=1,
)
''')

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_sysroot_prefix_cfgcall_valid_path(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    sysroot_prefix = Path('myprefix'),
)
''')

        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.sysroot_prefix, '/myprefix')

    def test_prjconfig_sysroot_prefix_cfgcall_valid_str(self):
        self.setprjcfg('sysroot_prefix', '/myprefix')
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.sysroot_prefix, '/myprefix')

    def test_prjconfig_sysroot_prefix_global_invalid(self):
        self.setprjcfg('sysroot_prefix', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_sysroot_prefix_global_valid_path(self):
        self.writeprjcfg('''\
from pathlib import Path
sysroot_prefix = Path('myprefix')
''')
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.sysroot_prefix, '/myprefix')

    def test_prjconfig_sysroot_prefix_global_valid_str(self):
        self.setprjcfg('sysroot_prefix', '/myprefix')
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.sysroot_prefix, '/myprefix')
