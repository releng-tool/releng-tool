# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool import __version__ as releng_version
from releng_tool.exceptions import RelengToolUnknownAction
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import redirect_stdout
from tests import run_testenv
import os


class TestEngineRunActions(RelengToolTestCase):
    def test_engine_run_actions_invalid_init(self):
        config = {
            'action': 'init',
        }

        # init should fail if we already have a project
        rv = run_testenv(config=config, template='minimal')
        self.assertFalse(rv)

    def test_engine_run_actions_valid_init(self):
        config = {
            'action': 'init',
        }

        with prepare_testenv(config=config) as engine:
            root_dir = engine.opts.root_dir
            releng_script = os.path.join(root_dir, 'releng-tool.rt')
            self.assertFalse(os.path.exists(releng_script))

            rv = engine.run()
            self.assertTrue(rv)
            self.assertTrue(os.path.exists(releng_script))

    def test_engine_run_actions_unknown_action(self):
        config = {
            'action': 'unknown-package',
        }

        with self.assertRaises(RelengToolUnknownAction):
            run_testenv(config=config, template='minimal')

    def test_engine_run_actions_valid_action_fetch(self):
        config = {
            'action': 'fetch',
        }

        rv = run_testenv(config=config, template='minimal')
        self.assertTrue(rv)

    def test_engine_run_actions_valid_action_state(self):
        config = {
            'action': 'state',
        }

        with redirect_stdout() as stream:
            rv = run_testenv(config=config, template='minimal')
        self.assertTrue(rv)

        # ensure state always dump's releng-tool's version
        self.assertIn(releng_version, stream.getvalue())

    def test_engine_run_actions_valid_package(self):
        config = {
            'action': 'minimal',
        }

        rv = run_testenv(config=config, template='minimal')
        self.assertTrue(rv)

    def test_engine_run_actions_valid_package_subaction(self):
        config = {
            'action': 'minimal-fetch',
        }

        rv = run_testenv(config=config, template='minimal')
        self.assertTrue(rv)
