# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests import setprjcfg
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsLintMaxVersion(TestDefaultEngineBase):
    def test_prjconfig_lint_max_version_invalid_type(self):
        setprjcfg(self.engine, 'lint_max_version', value=True)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_lint_max_version_invalid_value(self):
        setprjcfg(self.engine, 'lint_max_version', '1.2a')

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_lint_max_version_valid(self):
        setprjcfg(self.engine, 'lint_max_version', '1.2.3')
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.lint_max_version, [1, 2, 3])
