# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
from tests.support import fetch_unittest_assets_dir
import os


class TestEngineSubdir(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        cls.template_base = 'subdir'

        sample_files = fetch_unittest_assets_dir('sample-files')
        archive = os.path.join(sample_files, 'sample-files.tar')
        cls.site = f'TEST_SITE=r"file:///{archive}"'

    def test_engine_run_subdir_valid_bootstrap(self):
        template = os.path.join(self.template_base, 'subdir-valid-bootstrap')
        with prepare_testenv(template=template) as engine:
            root_dir = engine.opts.root_dir
            pkg_script = os.path.join(root_dir, 'package', 'test', 'test.rt')
            self.assertTrue(os.path.exists(pkg_script))

            with open(pkg_script, 'a') as f:
                f.write(self.site + '\n')

            rv = engine.run()
            self.assertTrue(rv)

            flag = os.path.join(engine.opts.target_dir, 'invoked-bootstrap')
            self.assertTrue(os.path.exists(flag))

    def test_engine_run_subdir_valid_configure(self):
        template = os.path.join(self.template_base, 'subdir-valid-configure')
        with prepare_testenv(template=template) as engine:
            root_dir = engine.opts.root_dir
            pkg_script = os.path.join(root_dir, 'package', 'test', 'test.rt')
            self.assertTrue(os.path.exists(pkg_script))

            with open(pkg_script, 'a') as f:
                f.write(self.site + '\n')

            rv = engine.run()
            self.assertTrue(rv)

            flag = os.path.join(engine.opts.target_dir, 'invoked-configure')
            self.assertTrue(os.path.exists(flag))

    def test_engine_run_subdir_valid_build(self):
        template = os.path.join(self.template_base, 'subdir-valid-build')
        with prepare_testenv(template=template) as engine:
            root_dir = engine.opts.root_dir
            pkg_script = os.path.join(root_dir, 'package', 'test', 'test.rt')
            self.assertTrue(os.path.exists(pkg_script))

            with open(pkg_script, 'a') as f:
                f.write(self.site + '\n')

            rv = engine.run()
            self.assertTrue(rv)

            flag = os.path.join(engine.opts.target_dir, 'invoked-build')
            self.assertTrue(os.path.exists(flag))

    def test_engine_run_subdir_valid_install(self):
        template = os.path.join(self.template_base, 'subdir-valid-install')
        with prepare_testenv(template=template) as engine:
            root_dir = engine.opts.root_dir
            pkg_script = os.path.join(root_dir, 'package', 'test', 'test.rt')
            self.assertTrue(os.path.exists(pkg_script))

            with open(pkg_script, 'a') as f:
                f.write(self.site + '\n')

            rv = engine.run()
            self.assertTrue(rv)

            flag = os.path.join(engine.opts.target_dir, 'invoked-install')
            self.assertTrue(os.path.exists(flag))

    def test_engine_run_subdir_valid_post(self):
        template = os.path.join(self.template_base, 'subdir-valid-post')
        with prepare_testenv(template=template) as engine:
            root_dir = engine.opts.root_dir
            pkg_script = os.path.join(root_dir, 'package', 'test', 'test.rt')
            self.assertTrue(os.path.exists(pkg_script))

            with open(pkg_script, 'a') as f:
                f.write(self.site + '\n')

            rv = engine.run()
            self.assertTrue(rv)

            flag = os.path.join(engine.opts.target_dir, 'invoked-post')
            self.assertTrue(os.path.exists(flag))
