# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestEngineRunSteps(RelengToolTestCase):
    def test_engine_run_steps(self):
        with prepare_testenv(template='steps') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flag = os.path.join(engine.opts.target_dir, 'invoked-1')
            self.assertTrue(os.path.exists(file_flag))

            file_flag = os.path.join(engine.opts.target_dir, 'invoked-2')
            self.assertFalse(os.path.exists(file_flag))

            file_flag = os.path.join(engine.opts.target_dir, 'invoked-3')
            self.assertTrue(os.path.exists(file_flag))
