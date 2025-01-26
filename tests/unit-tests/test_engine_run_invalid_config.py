# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationScript
from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from releng_tool.exceptions import RelengToolInvalidOverrideConfigurationScript
from tests import RelengToolTestCase
from tests import run_testenv


class TestEngineRunInvalidConfig(RelengToolTestCase):
    def test_engine_run_invalid_config_override(self):
        with self.assertRaises(RelengToolInvalidOverrideConfigurationScript):
            run_testenv(template='invalid-override-config')

    def test_engine_run_invalid_config_settings(self):
        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            run_testenv(template='invalid-project-settings')

    def test_engine_run_invalid_config_root(self):
        with self.assertRaises(RelengToolInvalidConfigurationScript):
            run_testenv(template='invalid-project-config')
