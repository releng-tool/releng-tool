# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestEngineRunStageWorkdir(RelengToolTestCase):
    def test_engine_run_stage_workdir_default(self):
        with prepare_testenv(template='stage-workdir') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flags = [
                os.path.join(engine.opts.target_dir, 'verified-bootstrap'),
                os.path.join(engine.opts.target_dir, 'verified-configure'),
                os.path.join(engine.opts.target_dir, 'verified-build'),
                os.path.join(engine.opts.target_dir, 'verified-install'),
                os.path.join(engine.opts.target_dir, 'verified-patch'),
                os.path.join(engine.opts.target_dir, 'verified-post'),
            ]

            for file_flag in file_flags:
                self.assertTrue(os.path.exists(file_flag), file_flag)

    def test_engine_run_stage_workdir_patch(self):
        with prepare_testenv(template='stage-workdir-patch') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flag = os.path.join(engine.opts.target_dir, 'verified-patch')
            self.assertTrue(os.path.exists(file_flag))
