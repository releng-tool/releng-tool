# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests import setprjcfg
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsPrerequisites(TestDefaultEngineBase):
    def test_prjconfig_prerequisites_invalid(self):
        setprjcfg(self.engine, 'prerequisites', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_prerequisites_valid_list(self):
        setprjcfg(self.engine, 'prerequisites', [
            'bin1',
            'bin2',
            'bin3',
        ])
        self.engine.run()

        opts = self.engine.opts
        self.assertIn('bin1', opts.prerequisites)
        self.assertIn('bin2', opts.prerequisites)
        self.assertIn('bin3', opts.prerequisites)

    def test_prjconfig_prerequisites_valid_str(self):
        setprjcfg(self.engine, 'prerequisites', 'myapp')
        self.engine.run()

        opts = self.engine.opts
        self.assertIn('myapp', opts.prerequisites)
