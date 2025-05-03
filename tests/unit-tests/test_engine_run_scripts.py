# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import run_testenv
import os


class TestEngineRunScripts(RelengToolTestCase):
    def test_engine_run_scripts_include(self):
        with prepare_testenv(template='scripts-include') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flags = [
                os.path.join(engine.opts.target_dir, 'invoked-stage1'),
                os.path.join(engine.opts.target_dir, 'invoked-stage2'),
                os.path.join(engine.opts.target_dir, 'invoked-stage3'),
                os.path.join(engine.opts.target_dir, 'invoked-stage4'),
                os.path.join(engine.opts.target_dir, 'invoked-stage5'),
            ]

            for file_flag in file_flags:
                self.assertTrue(os.path.exists(file_flag))

    def test_engine_run_scripts_invalid_bootstrap(self):
        rv = run_testenv(template='scripts-invalid-bootstrap')
        self.assertFalse(rv)

    def test_engine_run_scripts_invalid_build(self):
        rv = run_testenv(template='scripts-invalid-build')
        self.assertFalse(rv)

    def test_engine_run_scripts_invalid_configure(self):
        rv = run_testenv(template='scripts-invalid-configure')
        self.assertFalse(rv)

    def test_engine_run_scripts_invalid_install(self):
        rv = run_testenv(template='scripts-invalid-install')
        self.assertFalse(rv)

    def test_engine_run_scripts_invalid_post(self):
        rv = run_testenv(template='scripts-invalid-post')
        self.assertFalse(rv)

    def test_engine_run_scripts_valid_default(self):
        with prepare_testenv(template='scripts-valid') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flags = [
                os.path.join(engine.opts.target_dir, 'invoked-bootstrap'),
                os.path.join(engine.opts.target_dir, 'invoked-configure'),
                os.path.join(engine.opts.target_dir, 'invoked-build'),
                os.path.join(engine.opts.target_dir, 'invoked-install'),
                os.path.join(engine.opts.target_dir, 'invoked-patch'),
                os.path.join(engine.opts.target_dir, 'invoked-post'),
            ]

            for file_flag in file_flags:
                self.assertTrue(os.path.exists(file_flag))

    def test_engine_run_scripts_valid_ext_none(self):
        with prepare_testenv(template='scripts-valid-ext-none') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flags = [
                os.path.join(engine.opts.target_dir, 'invoked-bootstrap'),
                os.path.join(engine.opts.target_dir, 'invoked-configure'),
                os.path.join(engine.opts.target_dir, 'invoked-build'),
                os.path.join(engine.opts.target_dir, 'invoked-install'),
                os.path.join(engine.opts.target_dir, 'invoked-patch'),
                os.path.join(engine.opts.target_dir, 'invoked-post'),
            ]

            for file_flag in file_flags:
                self.assertTrue(os.path.exists(file_flag))

    def test_engine_run_scripts_valid_ext_py(self):
        with prepare_testenv(template='scripts-valid-ext-py') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flags = [
                os.path.join(engine.opts.target_dir, 'invoked-bootstrap'),
                os.path.join(engine.opts.target_dir, 'invoked-configure'),
                os.path.join(engine.opts.target_dir, 'invoked-build'),
                os.path.join(engine.opts.target_dir, 'invoked-install'),
                os.path.join(engine.opts.target_dir, 'invoked-patch'),
                os.path.join(engine.opts.target_dir, 'invoked-post'),
            ]

            for file_flag in file_flags:
                self.assertTrue(os.path.exists(file_flag))

    def test_engine_run_scripts_valid_ext_releng(self):
        with prepare_testenv(template='scripts-valid-ext-releng') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flags = [
                os.path.join(engine.opts.target_dir, 'invoked-bootstrap'),
                os.path.join(engine.opts.target_dir, 'invoked-configure'),
                os.path.join(engine.opts.target_dir, 'invoked-build'),
                os.path.join(engine.opts.target_dir, 'invoked-install'),
                os.path.join(engine.opts.target_dir, 'invoked-patch'),
                os.path.join(engine.opts.target_dir, 'invoked-post'),
            ]

            for file_flag in file_flags:
                self.assertTrue(os.path.exists(file_flag))
