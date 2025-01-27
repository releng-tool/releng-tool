# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


class TestScriptEnv(RelengToolTestCase):
    def test_script_env(self):
        with prepare_testenv(template='scripts-env') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            target_dir = engine.opts.target_dir

            pkg_start_file = os.path.join(target_dir, 'pkg-start.json')
            pkg_end_file = os.path.join(target_dir, 'pkg-end.json')
            nested_file = os.path.join(target_dir, 'nested.json')
            self.assertTrue(os.path.exists(pkg_start_file))
            self.assertTrue(os.path.exists(pkg_end_file))
            self.assertTrue(os.path.exists(nested_file))

            pkg_container_dir = engine.opts.default_pkg_dir
            pkg_dir = os.path.join(pkg_container_dir, 'test')
            build_script = os.path.join(pkg_dir, 'test-build.rt')
            self.assertTrue(os.path.exists(build_script))

            nested_dir = os.path.join(pkg_dir, 'nested')
            nested_script = os.path.join(nested_dir, 'test-build-nested.rt')
            self.assertTrue(os.path.exists(nested_script))

            # verify build script path and parent path are configured
            with open(pkg_start_file) as f:
                data = json.load(f)
                self.assertIn('RELENG_SCRIPT', data)
                self.assertEqual(data['RELENG_SCRIPT'], build_script)
                self.assertIn('RELENG_SCRIPT_DIR', data)
                self.assertEqual(data['RELENG_SCRIPT_DIR'], pkg_dir)

            # check we using an include, the script/parent-dir updates
            with open(nested_file) as f:
                data = json.load(f)
                self.assertIn('RELENG_SCRIPT', data)
                self.assertEqual(data['RELENG_SCRIPT'], nested_script)
                self.assertIn('RELENG_SCRIPT_DIR', data)
                self.assertEqual(data['RELENG_SCRIPT_DIR'], nested_dir)

            # after coming back from an include, ensure original values are set
            with open(pkg_end_file) as f:
                data = json.load(f)
                self.assertIn('RELENG_SCRIPT', data)
                self.assertEqual(data['RELENG_SCRIPT'], build_script)
                self.assertIn('RELENG_SCRIPT_DIR', data)
                self.assertEqual(data['RELENG_SCRIPT_DIR'], pkg_dir)
