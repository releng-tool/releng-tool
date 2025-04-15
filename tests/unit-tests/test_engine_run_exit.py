# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import run_testenv


class TestEngineRunExit(RelengToolTestCase):
    def test_engine_run_exit(self):
        with self.assertRaises(SystemExit) as cm:
            run_testenv(template='exit')

        self.assertEqual(cm.exception.code, 3)
