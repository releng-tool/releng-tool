# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


# base folder for test extensions
EXT_PREFIX = 'tests.unit-tests.assets.extensions.'


class TestPrjConfigsExtensions(TestDefaultEngineBase):
    def test_prjconfig_extensions_invalid(self):
        self.setprjcfg('extensions', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_extensions_valid_list(self):
        self.setprjcfg('extensions', [
            f'{EXT_PREFIX}events',
            f'{EXT_PREFIX}pkg-events',
        ])

        self.engine.run()

        registry = self.engine.registry
        self.assertIn(f'{EXT_PREFIX}events', registry.extension)
        self.assertIn(f'{EXT_PREFIX}pkg-events', registry.extension)

    def test_prjconfig_extensions_valid_str(self):
        self.setprjcfg('extensions', f'{EXT_PREFIX}events')

        self.engine.run()

        registry = self.engine.registry
        self.assertIn(f'{EXT_PREFIX}events', registry.extension)
