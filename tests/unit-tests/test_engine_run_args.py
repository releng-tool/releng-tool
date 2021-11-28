# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from tests import prepare_testenv
from tests import prepare_workdir
import os
import unittest

class TestEngineRunArgs(unittest.TestCase):
    def test_engine_run_args_assets_dir(self):
        with prepare_workdir() as assets_dir:
            config = {
                'assets_dir': assets_dir,
            }

            with prepare_testenv(config=config) as engine:
                expected_cache_dir = os.path.join(assets_dir, 'cache')
                expected_dl_dir = os.path.join(assets_dir, 'dl')
                self.assertEqual(engine.opts.cache_dir, expected_cache_dir)
                self.assertEqual(engine.opts.dl_dir, expected_dl_dir)

    def test_engine_run_args_debug(self):
        config = {
            'debug': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.debug)

    def test_engine_run_args_mode_devmode(self):
        config = {
            'development': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.devmode)

    def test_engine_run_args_mode_localsrcs(self):
        config = {
            'local_sources': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.local_srcs)

    def test_engine_run_args_nocolorout(self):
        config = {
            'nocolorout': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.no_color_out)

    def test_engine_run_args_jobs(self):
        config = {
            'jobs': 4,
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.jobs, 4)
            self.assertEqual(engine.opts.jobsconf, 4)

    def test_engine_run_args_quirks(self):
        quirks = [
            '--quirk1',
            '--quirk2',
        ]

        config = {
            'quirk': list(quirks),
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.quirks, quirks)

    def test_engine_run_args_verbose(self):
        config = {
            'verbose': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.verbose)
