# -*- coding: utf-8 -*-
# Copyright 2021-2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.defs import GBL_LSRCS
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import prepare_workdir
import os


class TestEngineRunArgs(RelengToolTestCase):
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

    def test_engine_run_args_cache_dir(self):
        with prepare_workdir() as cache_dir:
            config = {
                'cache_dir': cache_dir,
            }

            with prepare_testenv(config=config) as engine:
                self.assertEqual(engine.opts.cache_dir, cache_dir)

    def test_engine_run_args_config_file(self):
        test_filename = 'test-config'

        # test full configuration path
        with prepare_workdir() as misc_dir:
            mock_config = os.path.join(misc_dir, test_filename)

            config = {
                'config': mock_config,
            }

            with prepare_testenv(config=config) as engine:
                self.assertEqual(engine.opts.conf_point, mock_config)

        # test relative to working directory path
        with prepare_workdir() as root_dir:
            config = {
                'config': test_filename,
                'root_dir': root_dir,
            }

            with prepare_testenv(config=config) as engine:
                mock_config = os.path.join(os.getcwd(), test_filename)
                self.assertEqual(engine.opts.conf_point, mock_config)

    def test_engine_run_args_debug(self):
        config = {
            'debug': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.debug)

    def test_engine_run_args_dl_dir(self):
        with prepare_workdir() as dl_dir:
            config = {
                'dl_dir': dl_dir,
            }

            with prepare_testenv(config=config) as engine:
                self.assertEqual(engine.opts.dl_dir, dl_dir)

    def test_engine_run_args_images_dir(self):
        with prepare_workdir() as images_dir:
            config = {
                'images_dir': images_dir,
            }

            with prepare_testenv(config=config) as engine:
                self.assertEqual(engine.opts.images_dir, images_dir)

    def test_engine_run_args_mode_devmode(self):
        config = {
            'development': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.devmode)

    def test_engine_run_args_mode_force(self):
        config = {
            'force': True,
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue(engine.opts.force)

    def test_engine_run_args_mode_localsrcs_default(self):
        config = {
            'local_sources': [
                # --local-sources set with no paths
                None,
            ],
        }

        with prepare_testenv(config=config, template='minimal') as engine:
            self.assertTrue(isinstance(engine.opts.local_srcs, dict))
            self.assertTrue(GBL_LSRCS in engine.opts.local_srcs)
            self.assertIsNone(engine.opts.local_srcs[GBL_LSRCS])

    def test_engine_run_args_mode_localsrcs_not_configured(self):
        with prepare_testenv(template='minimal') as engine:
            self.assertFalse(engine.opts.local_srcs)

    def test_engine_run_args_mode_localsrcs_overload_package(self):
        with prepare_workdir() as dir_a, prepare_workdir() as dir_b:
            config = {
                'local_sources': [
                    # --local-sources set to a specific path
                    dir_a,
                    # overriding path for the `multiple-b` package
                    'multiple-b@{}'.format(dir_b),
                ],
            }

            with prepare_testenv(config=config, template='multiple') as engine:
                self.assertTrue(isinstance(engine.opts.local_srcs, dict))
                self.assertTrue(GBL_LSRCS in engine.opts.local_srcs)
                self.assertEqual(engine.opts.local_srcs[GBL_LSRCS], dir_a)
                self.assertTrue('multiple-b' in engine.opts.local_srcs)
                self.assertEqual(engine.opts.local_srcs['multiple-b'], dir_b)

    def test_engine_run_args_mode_localsrcs_per_package(self):
        with prepare_workdir() as dir_a, prepare_workdir() as dir_b:
            config = {
                'local_sources': [
                    # explicit path set for `multiple-a` package
                    'multiple-a@{}'.format(dir_a),
                    # explicit path set for `multiple-b` package
                    'multiple-b@{}'.format(dir_b),
                ],
            }

            with prepare_testenv(config=config, template='multiple') as engine:
                self.assertTrue(isinstance(engine.opts.local_srcs, dict))
                self.assertFalse(GBL_LSRCS in engine.opts.local_srcs)
                self.assertTrue('multiple-a' in engine.opts.local_srcs)
                self.assertEqual(engine.opts.local_srcs['multiple-a'], dir_a)
                self.assertTrue(engine.opts.local_srcs)
                self.assertTrue('multiple-b' in engine.opts.local_srcs)
                self.assertEqual(engine.opts.local_srcs['multiple-b'], dir_b)
                self.assertTrue(engine.opts.local_srcs)

    def test_engine_run_args_mode_localsrcs_single_path(self):
        with prepare_workdir() as test_dir:
            config = {
                'local_sources': [
                    # explicit path set
                    test_dir,
                ],
            }

            with prepare_testenv(config=config, template='multiple') as engine:
                self.assertTrue(isinstance(engine.opts.local_srcs, dict))
                self.assertTrue(GBL_LSRCS in engine.opts.local_srcs)
                self.assertEqual(engine.opts.local_srcs[GBL_LSRCS], test_dir)

    def test_engine_run_args_mode_localsrcs_specific_package(self):
        with prepare_workdir() as test_dir:
            config = {
                'local_sources': [
                    # explicit path set for a single package
                    'multiple-b@{}'.format(test_dir),
                ],
            }

            with prepare_testenv(config=config, template='multiple') as engine:
                self.assertTrue(isinstance(engine.opts.local_srcs, dict))
                self.assertFalse(GBL_LSRCS in engine.opts.local_srcs)
                self.assertTrue('multiple-b' in engine.opts.local_srcs)
                self.assertEqual(engine.opts.local_srcs['multiple-b'], test_dir)
                self.assertTrue(engine.opts.local_srcs)

    def test_engine_run_args_mode_localsrcs_unset_package(self):
        config = {
            'local_sources': [
                # --local-sources set to a specific path
                None,
                # clearing path for the `multiple-b` package
                'multiple-b@',
            ],
        }

        with prepare_testenv(config=config, template='multiple') as engine:
            self.assertTrue(isinstance(engine.opts.local_srcs, dict))
            self.assertTrue(GBL_LSRCS in engine.opts.local_srcs)
            self.assertIsNone(engine.opts.local_srcs[GBL_LSRCS])
            self.assertTrue('multiple-b' in engine.opts.local_srcs)
            self.assertIsNone(engine.opts.local_srcs['multiple-b'])

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

    def test_engine_run_args_out_dir(self):
        with prepare_workdir() as out_dir:
            config = {
                'out_dir': out_dir,
            }

            with prepare_testenv(config=config) as engine:
                self.assertEqual(engine.opts.out_dir, out_dir)

    def test_engine_run_args_sbom_format(self):
        config = {
            'sbom_format': 'html,json',
        }

        with prepare_testenv(config=config) as engine:
            self.assertTrue('html' in engine.opts.sbom_format)
            self.assertTrue('json' in engine.opts.sbom_format)

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
