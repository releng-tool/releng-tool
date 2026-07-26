# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsLintMaxVersion(TestDefaultEngineBase):
    def test_prjconfig_lint_max_version_global_invalid_type(self):
        self.setprjcfg('lint_max_version', value=True)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_lint_max_version_global_invalid_value(self):
        self.setprjcfg('lint_max_version', '1.2a')

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_lint_max_version_global_valid(self):
        self.setprjcfg('lint_max_version', '1.2.3')
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.lint_max_version, [1, 2, 3])
