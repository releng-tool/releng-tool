# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os
import unittest


class TestExtensionInjectEnvironment(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        if os.getenv('RELENG_SKIP_PY27_EXTENSION_TEST'):
            raise unittest.SkipTest('skipping extension test (py27-release)')

    def test_extension_inject_env(self):
        with prepare_testenv(template='extension-env-inject') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            sts = os.path.join(engine.opts.target_dir, 'status.json')
            self.assertTrue(os.path.exists(sts))

            with open(sts) as f:
                data = json.load(f)
                self.assertTrue('custom-invoke' in data)
                self.assertEqual(data['custom-invoke'], 42)
