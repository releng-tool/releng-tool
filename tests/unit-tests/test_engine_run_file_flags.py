# -*- coding: utf-8 -*-
# Copyright 2021-2022 releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestEngineRunFileFlags(RelengToolTestCase):
    def test_engine_run_file_flag_devmode(self):
        config = {
            'development': True,
        }

        with prepare_testenv(config=config, template='minimal') as engine:
            engine.run()
            self.assertTrue(os.path.exists(engine.opts.ff_devmode))
