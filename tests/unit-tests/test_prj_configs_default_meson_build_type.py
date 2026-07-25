# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests import setprjcfg
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsDefaultMesonBuildType(TestDefaultEngineBase):
    def test_prjconfig_default_meson_build_type_invalid(self):
        setprjcfg(self.engine, 'default_meson_build_type', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_default_meson_build_type_valid(self):
        setprjcfg(self.engine, 'default_meson_build_type', value='MyBuildType')
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.default_meson_build_type, 'MyBuildType')
