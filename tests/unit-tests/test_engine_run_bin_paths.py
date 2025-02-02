# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io import run_script
from tests import RelengToolTestCase
from tests import prepare_testenv
import os
import sys


class TestEngineRunBinPaths(RelengToolTestCase):
    def test_engine_run_bin_paths_host_output_custom_prefix(self):
        with prepare_testenv(template='hosts-check-prefix') as engine:
            engine.run()

            expected = 'releng-tool-test-script-custom'
            self._validate_test_script(expected)

    def test_engine_run_bin_paths_host_output_default_prefix(self):
        with prepare_testenv(template='hosts-check') as engine:
            engine.run()

            expected = 'releng-tool-test-script-bin'
            self._validate_test_script(expected)

    def test_engine_run_bin_paths_host_output_root(self):
        with prepare_testenv(template='hosts-check') as engine:
            engine.run()

            expected = 'releng-tool-test-script-host'
            self._validate_test_script(expected)

    def test_engine_run_bin_paths_project_root(self):
        with prepare_testenv(template='hosts-check') as engine:
            engine.run()

            expected = 'releng-tool-test-script-root'
            self._validate_test_script(expected)

    def _validate_test_script(self, name):
        gbls = {}

        for path in sys.path:
            script = os.path.join(path, name)

            if os.path.exists(script):
                gbls = run_script(script, gbls, catch=False)
                break

        self.assertIsNotNone(gbls)
        self.assertIn('var', gbls)
        self.assertEqual(gbls['var'], name)
