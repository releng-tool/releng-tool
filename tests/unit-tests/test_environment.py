# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool import __version__ as releng_version
from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


class TestEnvironment(RelengToolTestCase):
    def test_environment_project_injection(self):
        with prepare_testenv(template='env-inject') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            # extract environment variables
            capture = os.path.join(engine.opts.target_dir, 'invoke-env.json')
            self.assertTrue(os.path.exists(capture))

            with open(capture) as f:
                data = json.load(f)

            # sanity check one entry
            self.assertIn('TEST_1', data)
            self.assertEqual(data['TEST_1'], 'A')

            # and another to show more than one
            self.assertIn('TEST_2', data)
            self.assertEqual(data['TEST_2'], 'B')

            # also confirm variable expansion works
            self.assertIn('TEST_3', data)
            self.assertEqual(data['TEST_3'], releng_version)
