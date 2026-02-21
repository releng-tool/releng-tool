# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from contextlib import contextmanager
from releng_tool.__main__ import main
from tests import RelengToolTestCase
from unittest.mock import patch
import os


class TestMainlineColor(RelengToolTestCase):
    def test_mainline_color_force_disabled(self):
        with self._setup() as engine:
            os.environ['NO_COLOR'] = '1'
            main()
            opts = engine.call_args.args[0]
            self.assertTrue(opts.no_color_out)

    def test_mainline_color_force_enabled(self):
        with self._setup() as engine:
            os.environ['FORCE_COLOR'] = '1'
            os.environ['NO_COLOR'] = '1'
            main()
            opts = engine.call_args.args[0]
            self.assertFalse(opts.no_color_out)

    @contextmanager
    def _setup(self, *, rv: bool = True):
        with patch('releng_tool.__main__.RelengEngine') as engine, \
                patch('releng_tool.__main__.releng_log_configuration'):
            engine.return_value.run.return_value = rv
            yield engine
