# -*- coding: utf-8 -*-
# Copyright 2021-2022 releng-tool

from releng_tool.packages.exceptions import RelengToolMissingPackageScript
from tests import RelengToolTestCase
from tests import prepare_testenv
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
            releng_script = os.path.join(root_dir, 'releng')
            self.assertFalse(os.path.exists(releng_script))

            rv = engine.run()
            self.assertTrue(rv)
            self.assertTrue(os.path.exists(releng_script))

    def test_engine_run_actions_unknown_package(self):
        config = {
            'action': 'unknown-package',
        }

        with self.assertRaises(RelengToolMissingPackageScript):
            run_testenv(config=config, template='minimal')

    def test_engine_run_actions_valid_action(self):
        config = {
            'action': 'fetch',
        }

        rv = run_testenv(config=config, template='minimal')
        self.assertTrue(rv)

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
