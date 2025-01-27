# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import GBL_LSRCS
from releng_tool.defs import GlobalAction
from releng_tool.defs import PkgAction
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import prepare_workdir
import os


class TestEngineRunArgs(RelengToolTestCase):
    def test_engine_run_args_action_global_clean(self):
        config = {
            'action': 'clean',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, GlobalAction.CLEAN)

    def test_engine_run_args_action_global_distclean(self):
        config = {
            'action': 'distclean',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, GlobalAction.DISTCLEAN)

    def test_engine_run_args_action_global_extract(self):
        config = {
            'action': 'extract',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, GlobalAction.EXTRACT)

    def test_engine_run_args_action_global_fetch(self):
        config = {
            'action': 'fetch',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, GlobalAction.FETCH)

    def test_engine_run_args_action_global_init(self):
        config = {
            'action': 'init',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, GlobalAction.INIT)

    def test_engine_run_args_action_global_licenses(self):
        config = {
            'action': 'licenses',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, GlobalAction.LICENSES)

    def test_engine_run_args_action_global_mrproper(self):
        config = {
            'action': 'mrproper',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, GlobalAction.MRPROPER)

    def test_engine_run_args_action_global_patch(self):
        config = {
            'action': 'patch',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, GlobalAction.PATCH)

    def test_engine_run_args_action_global_punch(self):
        config = {
            'action': 'punch',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, GlobalAction.PUNCH)

    def test_engine_run_args_action_global_sbom(self):
        config = {
            'action': 'sbom',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, GlobalAction.SBOM)

    def test_engine_run_args_action_global_state(self):
        config = {
            'action': 'state',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, GlobalAction.STATE)

    def test_engine_run_args_action_pkg_build(self):
        config = {
            'action': 'test-build',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.BUILD)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_clean(self):
        config = {
            'action': 'test-clean',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.CLEAN)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_configure(self):
        config = {
            'action': 'test-configure',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.CONFIGURE)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_distclean(self):
        config = {
            'action': 'test-distclean',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.DISTCLEAN)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_exec(self):
        config = {
            'action': 'test-exec',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.EXEC)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_extract(self):
        config = {
            'action': 'test-extract',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.EXTRACT)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_fetch(self):
        config = {
            'action': 'test-fetch',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.FETCH)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_install(self):
        config = {
            'action': 'test-install',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.INSTALL)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_license(self):
        config = {
            'action': 'test-license',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.LICENSE)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_patch(self):
        config = {
            'action': 'test-patch',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.PATCH)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_rebuild(self):
        config = {
            'action': 'test-rebuild',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.REBUILD)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_rebuild_only(self):
        config = {
            'action': 'test-rebuild_only',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.REBUILD_ONLY)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_reconfigure(self):
        config = {
            'action': 'test-reconfigure',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.RECONFIGURE)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_reconfigure_only(self):
        config = {
            'action': 'test-reconfigure_only',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(
                engine.opts.pkg_action, PkgAction.RECONFIGURE_ONLY)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_pkg_reinstall(self):
        config = {
            'action': 'test-reinstall',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.pkg_action, PkgAction.REINSTALL)
            self.assertEqual(engine.opts.target_action, 'test')

    def test_engine_run_args_action_target_default(self):
        config = {
            'action': 'example',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, None)
            self.assertEqual(engine.opts.pkg_action, None)
            self.assertEqual(engine.opts.target_action, 'example')

    def test_engine_run_args_action_target_prefixed(self):
        config = {
            'action': 'package/another',
        }

        with prepare_testenv(config=config) as engine:
            self.assertEqual(engine.opts.gbl_action, None)
            self.assertEqual(engine.opts.pkg_action, None)
            self.assertEqual(engine.opts.target_action, 'another')

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
                self.assertEqual(engine.opts.conf_point, test_filename)

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
                    f'multiple-b@{dir_b}',
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
                    f'multiple-a@{dir_a}',
                    # explicit path set for `multiple-b` package
                    f'multiple-b:{dir_b}',
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
                    f'multiple-b:{test_dir}',
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

    def test_engine_run_args_output_dir(self):
        with prepare_workdir() as output_dir:
            config = {
                'output_dir': output_dir,
            }

            with prepare_testenv(config=config) as engine:
                self.assertEqual(engine.opts.out_dir, output_dir)

    def test_engine_run_args_output_directory_priority(self):
        with prepare_workdir() as out_dir, prepare_workdir() as output_dir:
            config = {
                'out_dir': out_dir,
                'output_dir': output_dir,
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
