# -*- coding: utf-8 -*-
# Copyright 2022 releng-tool

from tests import prepare_testenv
import os
import unittest
from releng_tool.exceptions import RelengToolMissingExecCommand


class TestEngineExec(unittest.TestCase):
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
