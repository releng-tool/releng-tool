# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.exceptions import RelengToolMissingExecCommand
from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


class TestEngineExec(RelengToolTestCase):
    def test_engine_run_exec_arg_missing(self):
        config = {
            'action': 'test-exec',
        }

        with prepare_testenv(config=config, template='exec') as engine:
            with self.assertRaises(RelengToolMissingExecCommand):
                engine.run()

    def test_engine_run_exec_failed(self):
        config = {
            'action': 'test-exec',
            'action_exec': 'python fail.py',
        }

        with prepare_testenv(config=config, template='exec') as engine:
            rv = engine.run()
            self.assertFalse(rv)

            flag = os.path.join(engine.opts.target_dir, 'invoked-fail')
            self.assertTrue(os.path.exists(flag))

    def test_engine_run_exec_flag_not_set(self):
        with prepare_testenv(template='exec-flag') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            # verify specific variables were set
            results = os.path.join(engine.opts.out_dir, 'invoke-vars.json')
            self.assertTrue(os.path.exists(results))

            with open(results, 'r') as f:
                data = json.load(f)

            # check that the revision has been overridden
            self.assertTrue('RELENG_EXEC' in data)
            self.assertFalse(data['RELENG_EXEC'])

    def test_engine_run_exec_flag_set(self):
        config = {
            'action': 'test-exec',
            'action_exec': 'python noop.py',
        }

        with prepare_testenv(config=config, template='exec-flag') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            # verify specific variables were set
            results = os.path.join(engine.opts.out_dir, 'invoke-vars.json')
            self.assertTrue(os.path.exists(results))

            with open(results, 'r') as f:
                data = json.load(f)

            # check that the revision has been overridden
            self.assertTrue('RELENG_EXEC' in data)
            self.assertTrue(data['RELENG_EXEC'])

    def test_engine_run_exec_success(self):
        config = {
            'action': 'test-exec',
            'action_exec': 'python success.py',
        }

        with prepare_testenv(config=config, template='exec') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            flag = os.path.join(engine.opts.target_dir, 'invoked-success')
            self.assertTrue(os.path.exists(flag))
