# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsCacheExt(TestDefaultEngineBase):
    def test_prjconfig_external_packages_cfgcall_invalid(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    external_packages=1,
)
''')

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_external_packages_cfgcall_valid(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    external_packages=[
        'path1',
        'path2',
    ],
)
''')

        self.engine.run()

        opts = self.engine.opts
        self.assertIsNotNone(opts.extern_pkg_dirs)
        self.assertEqual(len(opts.extern_pkg_dirs), 2)
        self.assertIn('path1', opts.extern_pkg_dirs)
        self.assertIn('path2', opts.extern_pkg_dirs)

    def test_prjconfig_external_packages_global_invalid(self):
        self.setprjcfg('external_packages', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_external_packages_global_valid(self):
        self.writeprjcfg('''\
external_packages = [
    'path1',
    'path2',
]
''')
        self.engine.run()

        opts = self.engine.opts
        self.assertIsNotNone(opts.extern_pkg_dirs)
        self.assertEqual(len(opts.extern_pkg_dirs), 2)
        self.assertIn('path1', opts.extern_pkg_dirs)
        self.assertIn('path2', opts.extern_pkg_dirs)
