# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestEngineEnvArgs(RelengToolTestCase):
    def test_engine_env_args_quirks_multiple_comma(self):
        expected_quirks = [
            'quirk.opt.1',
            'quirk.opt.2',
        ]

        os.environ['RELENG_QUIRKS'] = 'quirk.opt.1,quirk.opt.2'

        with prepare_testenv() as engine:
            self.assertEqual(engine.opts.quirks, expected_quirks)

    def test_engine_env_args_quirks_multiple_semicolon(self):
        expected_quirks = [
            'quirk.opt.1',
            'quirk.opt.2',
        ]

        os.environ['RELENG_QUIRKS'] = 'quirk.opt.1;quirk.opt.2'

        with prepare_testenv() as engine:
            self.assertEqual(engine.opts.quirks, expected_quirks)

    def test_engine_env_args_quirks_multiple_space(self):
        expected_quirks = [
            'quirk.opt.1',
            'quirk.opt.2',
        ]

        os.environ['RELENG_QUIRKS'] = 'quirk.opt.1 quirk.opt.2'

        with prepare_testenv() as engine:
            self.assertEqual(engine.opts.quirks, expected_quirks)

    def test_engine_env_args_quirks_single(self):
        expected_quirks = [
            'quirk_opt',
        ]

        os.environ['RELENG_QUIRKS'] = 'quirk_opt'

        with prepare_testenv() as engine:
            self.assertEqual(engine.opts.quirks, expected_quirks)
