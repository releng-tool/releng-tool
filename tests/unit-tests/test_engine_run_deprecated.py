# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestEngineRunDeprecated(RelengToolTestCase):
    def test_engine_run_deprecated_post_build_1(self):
        with prepare_testenv(
                template='deprecated-post-build-1') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flag = os.path.join(engine.opts.out_dir, 'invoked-post')
            self.assertTrue(os.path.exists(file_flag))

    def test_engine_run_deprecated_post_build_2(self):
        with prepare_testenv(
                template='deprecated-post-build-2') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flag = os.path.join(engine.opts.out_dir, 'invoked-post')
            self.assertTrue(os.path.exists(file_flag))

    def test_engine_run_deprecated_post_build_3(self):
        with prepare_testenv(
                template='deprecated-post-build-3') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flag = os.path.join(engine.opts.out_dir, 'invoked-post')
            self.assertTrue(os.path.exists(file_flag))

    def test_engine_run_deprecated_cfg_ext_none(self):
        with prepare_testenv(
                template='deprecated-project-cfg-ext-none') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flag = os.path.join(engine.opts.out_dir, 'invoked-build')
            self.assertTrue(os.path.exists(file_flag))

    def test_engine_run_deprecated_cfg_ext_py(self):
        with prepare_testenv(
                template='deprecated-project-cfg-ext-py') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flag = os.path.join(engine.opts.out_dir, 'invoked-build')
            self.assertTrue(os.path.exists(file_flag))

    def test_engine_run_deprecated_cfg_ext_releng(self):
        with prepare_testenv(
                template='deprecated-project-cfg-ext-releng') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flag = os.path.join(engine.opts.out_dir, 'invoked-build')
            self.assertTrue(os.path.exists(file_flag))
