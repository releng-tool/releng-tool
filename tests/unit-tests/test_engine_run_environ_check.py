# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import run_testenv
import os


class TestEngineRunEnvironCheck(RelengToolTestCase):
    def test_engine_run_environ_check_defaults(self):
        rv = run_testenv(template='env-defaults')
        self.assertTrue(rv)

        optional_env_vars = [
            'RELENG_CLEAN',
            'RELENG_DEBUG',
            'RELENG_DEVMODE',
            'RELENG_DISTCLEAN',
            'RELENG_EXEC',
            'RELENG_FORCE',
            'RELENG_LOCALSRCS',
            'RELENG_MRPROPER',
            'RELENG_PROFILES',
            'RELENG_REBUILD',
            'RELENG_RECONFIGURE',
            'RELENG_REINSTALL',
            'RELENG_TARGET_PKG',
            'RELENG_VERBOSE',
        ]

        for var in optional_env_vars:
            self.assertFalse(var in os.environ, var)

    def test_engine_run_environ_check_target_pkg(self):
        config = {
            'action': 'minimal-fetch',
        }

        rv = run_testenv(config=config, template='minimal')
        self.assertTrue(rv)

        self.assertTrue('RELENG_TARGET_PKG' in os.environ)
        target_pkg = os.environ['RELENG_TARGET_PKG']
        self.assertEqual(target_pkg, 'minimal')
