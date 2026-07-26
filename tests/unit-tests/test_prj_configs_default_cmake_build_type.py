# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsDefaultCmakeBuildType(TestDefaultEngineBase):
    def test_prjconfig_default_cmake_build_type_invalid(self):
        self.setprjcfg('default_cmake_build_type', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_default_cmake_build_type_valid(self):
        self.setprjcfg('default_cmake_build_type', value='MyBuildType')
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.default_cmake_build_type, 'MyBuildType')
