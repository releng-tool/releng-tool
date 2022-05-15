# -*- coding: utf-8 -*-
# Copyright 2022 releng-tool

from tests import run_testenv
from tests.support.env_test import EnvironmentTestCase
import os


class TestEngineRunEnvironCheck(EnvironmentTestCase):
    def test_engine_run_environ_check_target_pkg(self):
        config = {
            'action': 'minimal-fetch',
        }

        rv = run_testenv(config=config, template='minimal')
        self.assertTrue(rv)

        self.assertTrue('RELENG_TARGET_PKG' in os.environ)
        target_pkg = os.environ['RELENG_TARGET_PKG']
        self.assertEqual(target_pkg, 'minimal')
