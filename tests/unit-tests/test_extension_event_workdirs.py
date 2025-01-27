# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os
import unittest


class TestExtensionEventWorkingDirectories(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        if os.getenv('RELENG_SKIP_PY27_EXTENSION_TEST'):
            raise unittest.SkipTest('skipping extension test (py27-release)')

    def test_extension_event_workdirs(self):
        with prepare_testenv(template='extension-env-dirs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected_workdirs = {
                'config-loaded': engine.opts.root_dir,
                'post-build-started': engine.opts.target_dir,
                'post-build-finished': engine.opts.target_dir,
            }

            for k, expected_dir in expected_workdirs.items():
                state = os.path.join(engine.opts.root_dir, k + '.json')
                self.assertTrue(os.path.exists(state))

                with open(state) as f:
                    data = json.load(f)
                    self.assertTrue('wd' in data)
                    self.assertEqual(os.path.realpath(data['wd']),
                        os.path.realpath(expected_dir))
