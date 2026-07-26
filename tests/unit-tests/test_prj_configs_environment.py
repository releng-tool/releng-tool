# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsEnvironment(TestDefaultEngineBase):
    def test_prjconfig_environment_cfgcall_invalid(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    environment=1,
)
''')

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_environment_cfgcall_valid(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    environment={
        'MY_ENV_1': 'First example',
        'MY_ENV_2': 'Another example',
    },
)
''')

        self.engine.run()

        opts = self.engine.opts
        self.assertIn('MY_ENV_1', opts.environment)
        self.assertEqual(opts.environment['MY_ENV_1'], 'First example')
        self.assertIn('MY_ENV_2', opts.environment)
        self.assertEqual(opts.environment['MY_ENV_2'], 'Another example')

    def test_prjconfig_environment_global_invalid(self):
        self.setprjcfg('environment', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_environment_global_valid(self):
        self.setprjcfg('environment', value={
            'MY_ENV_1': 'First example',
            'MY_ENV_2': 'Another example',
        })
        self.engine.run()

        opts = self.engine.opts
        self.assertIn('MY_ENV_1', opts.environment)
        self.assertEqual(opts.environment['MY_ENV_1'], 'First example')
        self.assertIn('MY_ENV_2', opts.environment)
        self.assertEqual(opts.environment['MY_ENV_2'], 'Another example')
