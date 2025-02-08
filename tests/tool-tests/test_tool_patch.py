# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
from tests.support import fetch_unittest_assets_dir
import os


class TestToolPatch(RelengToolTestCase):
    def test_tool_patch_invalid(self):
        with prepare_testenv(template='patch-file-invalid') as engine:
            rv = engine.run()
            self.assertFalse(rv)

    def test_tool_patch_subdir_build(self):
        with prepare_testenv(template='patch-file-build-subdir') as engine:
            # map to a sample archive, to have some a sub-directory to
            # jump to
            sample_files = fetch_unittest_assets_dir('sample-files')
            archive = os.path.join(sample_files, 'sample-files.tar')
            site = f'TEST_SITE=r"file:///{archive}"'

            root_dir = engine.opts.root_dir
            pkg_script = os.path.join(root_dir, 'package', 'test', 'test.rt')

            with open(pkg_script, 'a') as f:
                f.write(site + '\n')

            rv = engine.run()
            self.assertTrue(rv)

            # verify expected sample content first
            build_dir = os.path.join(engine.opts.build_dir, 'test')
            container_dir = os.path.join(build_dir, 'container')
            new_file = os.path.join(container_dir, 'tar-file-container.txt')
            self.assertTrue(os.path.exists(new_file))

            # valid patch was applied in the root directory
            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertTrue(os.path.exists(new_file))

            with open(new_file) as f:
                data = f.read()
                self.assertTrue('Sample file.' in data)

    def test_tool_patch_subdir_patch(self):
        with prepare_testenv(template='patch-file-patch-subdir') as engine:
            # map to a sample archive, to have some a sub-directory to
            # jump to
            sample_files = fetch_unittest_assets_dir('sample-files')
            archive = os.path.join(sample_files, 'sample-files.tar')
            site = f'TEST_SITE=r"file:///{archive}"'

            root_dir = engine.opts.root_dir
            pkg_script = os.path.join(root_dir, 'package', 'test', 'test.rt')
            self.assertTrue(os.path.exists(pkg_script))

            with open(pkg_script, 'a') as f:
                f.write(site + '\n')

            rv = engine.run()
            self.assertTrue(rv)

            # verify expected sample content first
            build_dir = os.path.join(engine.opts.build_dir, 'test')
            container_dir = os.path.join(build_dir, 'container')
            new_file = os.path.join(container_dir, 'tar-file-container.txt')
            self.assertTrue(os.path.exists(new_file))

            # valid patch was applied in the container directory
            new_file = os.path.join(container_dir, 'new-file.txt')
            self.assertTrue(os.path.exists(new_file))

            with open(new_file) as f:
                data = f.read()
                self.assertTrue('Sample file.' in data)

    def test_tool_patch_valid(self):
        with prepare_testenv(template='patch-file-valid') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test')
            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertTrue(os.path.exists(new_file))

            with open(new_file) as f:
                data = f.read()
                self.assertTrue('Sample file.' in data)
