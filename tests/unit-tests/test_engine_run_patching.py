# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestEngineRunPatching(RelengToolTestCase):
    def test_engine_run_patching_script_invalid(self):
        with prepare_testenv(template='patch-script-invalid') as engine:
            rv = engine.run()
            self.assertFalse(rv)

    def test_engine_run_patching_script_valid(self):
        with prepare_testenv(template='patch-script-valid') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flag = os.path.join(engine.opts.target_dir, 'invoked-patch')
            self.assertTrue(os.path.exists(file_flag))
