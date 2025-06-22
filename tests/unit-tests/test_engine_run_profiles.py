# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from tests import RelengToolTestCase
from tests import prepare_testenv
import json


class TestEngineRunProfiless(RelengToolTestCase):
    def test_engine_run_profiles_default(self):
        with prepare_testenv(template='profile-capture') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            # verify we got a capture
            results = Path(engine.opts.out_dir) / 'capture.json'
            self.assertTrue(results.is_file())

            with open(results) as f:
                data = json.load(f)

            # verify we have a local reference
            self.assertTrue('has-local' in data)
            self.assertTrue(data['has-local'])

            # also that the local data has no profiles
            self.assertTrue('local' in data)
            self.assertFalse(data['local'])

            # verify we do not have an environment entry
            self.assertTrue('has-env' in data)
            self.assertFalse(data['has-env'])

    def test_engine_run_profiles_multiple(self):
        cfg = {
            'profile': [
                'one',
                'two',
                'three',
            ],
        }

        with prepare_testenv(config=cfg, template='profile-capture') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            # verify we got a capture
            results = Path(engine.opts.out_dir) / 'capture.json'
            self.assertTrue(results.is_file())

            with open(results) as f:
                data = json.load(f)

            # verify we have a local reference
            self.assertTrue('has-local' in data)
            self.assertTrue(data['has-local'])

            # also that the local data our list of a single profile
            self.assertTrue('local' in data)
            self.assertEqual(data['local'], [
                'one',
                'two',
                'three',
            ])

            # verify we an environment entry
            self.assertTrue('has-env' in data)
            self.assertTrue(data['has-env'])

            # also that the local data has a string of the profiles
            self.assertTrue('env' in data)
            self.assertEqual(data['env'], 'one;two;three')

    def test_engine_run_profiles_single(self):
        cfg = {
            'profile': [
                'example',
            ],
        }

        with prepare_testenv(config=cfg, template='profile-capture') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            # verify we got a capture
            results = Path(engine.opts.out_dir) / 'capture.json'
            self.assertTrue(results.is_file())

            with open(results) as f:
                data = json.load(f)

            # verify we have a local reference
            self.assertTrue('has-local' in data)
            self.assertTrue(data['has-local'])

            # also that the local data our list of a single profile
            self.assertTrue('local' in data)
            self.assertEqual(data['local'], ['example'])

            # verify we an environment entry
            self.assertTrue('has-env' in data)
            self.assertTrue(data['has-env'])

            # also that the local data has a string of the profile
            self.assertTrue('env' in data)
            self.assertEqual(data['env'], 'example')
