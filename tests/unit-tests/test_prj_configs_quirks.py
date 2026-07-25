# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests import setprjcfg
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsQuirks(TestDefaultEngineBase):
    def test_prjconfig_quirks_invalid(self):
        setprjcfg(self.engine, 'quirks', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_quirks_valid_list(self):
        setprjcfg(self.engine, 'quirks', [
            'releng.quirk1',
            'releng.quirk2',
            'releng.quirk4',
        ])
        self.engine.run()

        opts = self.engine.opts
        self.assertIn('releng.quirk1', opts.quirks)
        self.assertIn('releng.quirk2', opts.quirks)
        self.assertIn('releng.quirk4', opts.quirks)

    def test_prjconfig_quirks_valid_str(self):
        setprjcfg(self.engine, 'quirks', 'releng.quirk3')
        self.engine.run()

        opts = self.engine.opts
        self.assertIn('releng.quirk3', opts.quirks)
