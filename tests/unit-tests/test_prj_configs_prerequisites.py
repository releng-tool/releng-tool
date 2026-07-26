# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsPrerequisites(TestDefaultEngineBase):
    def test_prjconfig_prerequisites_global_invalid(self):
        self.setprjcfg('prerequisites', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_prerequisites_global_valid_list(self):
        self.setprjcfg('prerequisites', [
            'bin1',
            'bin2',
            'bin3',
        ])
        self.engine.run()

        opts = self.engine.opts
        self.assertIn('bin1', opts.prerequisites)
        self.assertIn('bin2', opts.prerequisites)
        self.assertIn('bin3', opts.prerequisites)

    def test_prjconfig_prerequisites_global_valid_str(self):
        self.setprjcfg('prerequisites', 'myapp')
        self.engine.run()

        opts = self.engine.opts
        self.assertIn('myapp', opts.prerequisites)
