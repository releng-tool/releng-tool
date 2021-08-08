# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from releng_tool.packages.exceptions import RelengToolMissingPackageScript
from tests import run_testenv
import unittest

class TestEngineRunActions(unittest.TestCase):
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
