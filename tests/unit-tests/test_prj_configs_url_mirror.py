# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsUrlMirror(TestDefaultEngineBase):
    def test_prjconfig_url_mirror_invalid(self):
        self.setprjcfg('url_mirror', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_url_mirror_valid(self):
        expected_mirror = 'https://pkgs.example.com/{name}/'

        self.setprjcfg('url_mirror', expected_mirror)
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.url_mirror, expected_mirror)
