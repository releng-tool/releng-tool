# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests import setprjcfg
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsEnvironment(TestDefaultEngineBase):
    def test_prjconfig_environment_invalid(self):
        setprjcfg(self.engine, 'environment', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_environment_valid(self):
        setprjcfg(self.engine, 'environment', value={
            'MY_ENV_1': 'First example',
            'MY_ENV_2': 'Another example',
        })
        self.engine.run()

        opts = self.engine.opts
        self.assertIn('MY_ENV_1', opts.environment)
        self.assertEqual(opts.environment['MY_ENV_1'], 'First example')
        self.assertIn('MY_ENV_2', opts.environment)
        self.assertEqual(opts.environment['MY_ENV_2'], 'Another example')
