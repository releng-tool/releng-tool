# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolMissingConfigurationError
from releng_tool.exceptions import RelengToolMissingPackagesError
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import run_testenv
import os


class TestEngineRunDefaults(RelengToolTestCase):
    def test_engine_run_defaults_dirs(self):
        with prepare_testenv(template='minimal') as engine:
            # check if root directory is tracked
            root_dir = engine.opts.root_dir
            self.assertTrue(os.path.exists(root_dir))

            # ensure default paths for other directories are populated
            expected_cache_dir = os.path.join(root_dir, 'cache')
            expected_dl_dir = os.path.join(root_dir, 'dl')
            expected_out_dir = os.path.join(root_dir, 'output')
            self.assertEqual(engine.opts.cache_dir, expected_cache_dir)
            self.assertEqual(engine.opts.dl_dir, expected_dl_dir)
            self.assertEqual(engine.opts.out_dir, expected_out_dir)

    def test_engine_run_defaults_noconfig(self):
        with self.assertRaises(RelengToolMissingConfigurationError):
            run_testenv()

    def test_engine_run_defaults_nopackages(self):
        with self.assertRaises(RelengToolMissingPackagesError):
            run_testenv(template='no-packages')

    def test_engine_run_defaults_options_jobs(self):
        with prepare_testenv() as engine:
            self.assertNotEqual(engine.opts.jobs, 0)
            self.assertEqual(engine.opts.jobsconf, 0)

    def test_engine_run_defaults_options_logging(self):
        with prepare_testenv() as engine:
            self.assertFalse(engine.opts.debug)
            self.assertFalse(engine.opts.no_color_out)
            self.assertFalse(engine.opts.verbose)

    def test_engine_run_defaults_options_modes(self):
        with prepare_testenv() as engine:
            self.assertFalse(engine.opts.devmode)
            self.assertFalse(engine.opts.force)
            self.assertFalse(engine.opts.local_srcs)
