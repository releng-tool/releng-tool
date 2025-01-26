# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
from releng_tool.tool.vswhere import VSWHERE
import os
import sys
import unittest


class TestVsDevCmd(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        if sys.platform != 'win32':
            raise unittest.SkipTest('only win32')

        if not VSWHERE.exists():
            raise unittest.SkipTest('environment does not have vswhere')

    def test_vsdevcmd_global_default(self):
        with prepare_testenv(template='vsdevcmd-global-default') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            target_dir = engine.opts.target_dir

            expected_exists = [
                os.path.join(target_dir, 'build-success'),
                os.path.join(target_dir, 'post-build-success'),
            ]

            for expected in expected_exists:
                self.assertTrue(os.path.exists(expected), expected)

    def test_vsdevcmd_package_default(self):
        with prepare_testenv(template='vsdevcmd-package-default') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            target_dir = engine.opts.target_dir

            expected_exists = [
                os.path.join(target_dir, 'build-success'),
                os.path.join(target_dir, 'post-build-failure'),
            ]

            for expected in expected_exists:
                self.assertTrue(os.path.exists(expected), expected)
