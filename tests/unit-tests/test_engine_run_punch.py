# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import GlobalAction
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import prepare_workdir
import json
import os


class TestEngineRunPunch(RelengToolTestCase):
    def test_engine_run_punch_multipass_default(self):
        state = self._run_tripass()

        # in a default state, all stages run once excpet for post-run
        self.assertEqual(state['bootstrap'], 1)
        self.assertEqual(state['configure'], 1)
        self.assertEqual(state['build'], 1)
        self.assertEqual(state['install'], 1)
        self.assertEqual(state['post'], 1)
        self.assertEqual(state['post-run'], 3)

    def test_engine_run_punch_multipass_punched(self):
        state = self._run_tripass(action=GlobalAction.PUNCH)

        # verify each stage has been three times
        self.assertEqual(state['bootstrap'], 3)
        self.assertEqual(state['configure'], 3)
        self.assertEqual(state['build'], 3)
        self.assertEqual(state['install'], 3)
        self.assertEqual(state['post'], 3)
        self.assertEqual(state['post-run'], 3)

    def _run_tripass(self, action=None):
        with prepare_workdir() as output_dir:
            config = {
                'action': action,
                'output_dir': output_dir,
            }

            # first pass
            with prepare_testenv(config=config, template='punch') as engine:
                rv = engine.run()
                self.assertTrue(rv)

            # second pass
            with prepare_testenv(config=config, template='punch') as engine:
                rv = engine.run()
                self.assertTrue(rv)

            # third time is a charm
            with prepare_testenv(config=config, template='punch') as engine:
                out_dir = engine.opts.out_dir

                rv = engine.run()
                self.assertTrue(rv)

                # load state counters
                test_state_db = os.path.join(out_dir, 'state.json')
                self.assertTrue(os.path.exists(test_state_db))

                with open(test_state_db) as f:
                    return json.load(f)
