# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.engine.script_env import prepare_script_environment
from releng_tool.opts import RelengEngineOptions
from tests import RelengToolTestCase
import ast


class TestEngineScriptEnv(RelengToolTestCase):
    def setUp(self):
        self.opts = RelengEngineOptions()

    def test_engine_scriptenv_verify_utility_methods(self):
        # prepare a script environment
        env = {}
        prepare_script_environment(env, self.opts)

        # find the releng-tool module script helpers can be imported from
        root_dir = Path(__file__).parent.parent.parent
        rtm = root_dir / 'releng_tool' / '__init__.py'
        self.assertTrue(rtm.is_file())

        # read this file and extract all import aliases
        rtm_contents = rtm.read_text()
        tree = ast.parse(rtm_contents)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue

            # each alias should be found in the script environment
            for alias in node.names:
                self.assertIn(alias.asname, env)
