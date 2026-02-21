# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests import setprjcfg
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsUrlMirror(TestDefaultEngineBase):
    def test_prjconfig_url_mirror_invalid(self):
        setprjcfg(self.engine, 'url_mirror', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_url_mirror_valid(self):
        expected_mirror = 'https://pkgs.example.com/{name}/'

        setprjcfg(self.engine, 'url_mirror', expected_mirror)
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.url_mirror, expected_mirror)
