# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import prepare_workdir
import os


class TestEngineRunEnvironConfig(RelengToolTestCase):
    def test_engine_run_environ_cfg_assets_dir(self):
        with prepare_workdir() as assets_dir:
            os.environ['RELENG_ASSETS_DIR'] = assets_dir

            with prepare_testenv() as engine:
                expected_cache_dir = os.path.join(assets_dir, 'cache')
                expected_dl_dir = os.path.join(assets_dir, 'dl')
                self.assertEqual(engine.opts.cache_dir, expected_cache_dir)
                self.assertEqual(engine.opts.dl_dir, expected_dl_dir)

    def test_engine_run_environ_cfg_cache_dir(self):
        with prepare_workdir() as cache_dir:
            os.environ['RELENG_CACHE_DIR'] = cache_dir

            with prepare_testenv() as engine:
                self.assertEqual(engine.opts.cache_dir, cache_dir)

    def test_engine_run_environ_cfg_dl_dir(self):
        with prepare_workdir() as dl_dir:
            os.environ['RELENG_DL_DIR'] = dl_dir

            with prepare_testenv() as engine:
                self.assertEqual(engine.opts.dl_dir, dl_dir)

    def test_engine_run_environ_cfg_out_dir(self):
        with prepare_workdir() as out_dir:
            os.environ['RELENG_OUTPUT_DIR'] = out_dir

            with prepare_testenv() as engine:
                self.assertEqual(engine.opts.out_dir, out_dir)
