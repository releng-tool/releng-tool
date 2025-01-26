# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.runner import detect_ci_runner_debug_mode
from tests import RelengToolTestCase
import os


class TestUtilRunner(RelengToolTestCase):
    def test_utilrunner_cidebugdetect(self):
        with self.env_wrap():
            # pretend we are running in a debugging mode
            os.environ['ACTIONS_RUNNER_DEBUG'] = '1'

            self.assertTrue(detect_ci_runner_debug_mode())
