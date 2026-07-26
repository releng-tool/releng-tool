# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsCacheExt(TestDefaultEngineBase):
    def test_prjconfig_cache_ext_cfgcall_invalid(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    cache_ext=1,
)
''')

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_cache_ext_cfgcall_valid(self):
        self.newprjcfg('''\
def my_translator(site):
    if 'static.example.org' in site:
        return 'tgz'
    return None

releng_config(
    packages = [
        'minimal',
    ],
    cache_ext=my_translator,
)
''')

        self.engine.run()

        opts = self.engine.opts
        self.assertIsNotNone(opts.cache_ext_transform)
        self.assertTrue(callable(opts.cache_ext_transform))

        result = opts.cache_ext_transform('static.example.org')
        self.assertEqual(result, 'tgz')

    def test_prjconfig_cache_ext_global_invalid(self):
        self.setprjcfg('cache_ext', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_cache_ext_global_valid(self):
        self.writeprjcfg('''\
def my_translator(site):
    if 'static.example.org' in site:
        return 'tgz'
    return None

cache_ext = my_translator
''')
        self.engine.run()

        opts = self.engine.opts
        self.assertIsNotNone(opts.cache_ext_transform)
        self.assertTrue(callable(opts.cache_ext_transform))

        result = opts.cache_ext_transform('static.example.org')
        self.assertEqual(result, 'tgz')
