# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from contextlib import contextmanager
from releng_tool.__main__ import main
from tests import RelengToolTestCase
from tests import redirect_stdout
from unittest.mock import patch
import os


class TestMainlineArgs(RelengToolTestCase):
    def test_mainline_args_assets_dir_missing(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--assets-dir',
            ])

    def test_mainline_args_assets_dir_valid(self):
        with self._setup() as engine:
            main([
                '--assets-dir',
                'example-path',
            ])
            opts = engine.call_args.args[0]
            self.assertIn('example-path', opts.assets_dir)

    def test_mainline_args_cache_dir_missing(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--cache-dir',
            ])

    def test_mainline_args_cache_dir_valid(self):
        with self._setup() as engine:
            main([
                '--cache-dir',
                'example-path',
            ])
            opts = engine.call_args.args[0]
            self.assertIn('example-path', opts.cache_dir)

    def test_mainline_args_config_missing(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--config',
            ])

    def test_mainline_args_config_valid(self):
        with self._setup() as engine:
            main([
                '--config',
                'example-cfg',
            ])
            opts = engine.call_args.args[0]
            self.assertIn('example-cfg', opts.conf_point)

    def test_mainline_args_debug_basic(self):
        with self._setup() as engine:
            main([
                '--debug',
            ])
            opts = engine.call_args.args[0]
            self.assertTrue(opts.debug)
            self.assertFalse(opts.debug_extended)

    def test_mainline_args_debug_extended(self):
        with self._setup() as engine:
            main([
                '--debug-extended',
            ])
            opts = engine.call_args.args[0]
            self.assertTrue(opts.debug)
            self.assertTrue(opts.debug_extended)

    def test_mainline_args_devmode_custom(self):
        with self._setup() as engine:
            main([
                '--development',
                'custom',
            ])
            opts = engine.call_args.args[0]
            self.assertEqual(opts.devmode, 'custom')

    def test_mainline_args_devmode_flag(self):
        with self._setup() as engine:
            main([
                '--development',
            ])
            opts = engine.call_args.args[0]
            self.assertTrue(opts.devmode)

    def test_mainline_args_dl_dir_missing(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--dl-dir',
            ])

    def test_mainline_args_dl_dir_valid(self):
        with self._setup() as engine:
            main([
                '--dl-dir',
                'example-path',
            ])
            opts = engine.call_args.args[0]
            self.assertIn('example-path', opts.dl_dir)

    def test_mainline_args_force(self):
        with self._setup() as engine:
            main([
                '--force',
            ])
            opts = engine.call_args.args[0]
            self.assertTrue(opts.force)

    def test_mainline_args_fwd(self):
        with self._setup() as engine:
            main([
                '--',
                '--custom-argument',
            ])
            opts = engine.call_args.args[0]
            self.assertIn('--custom-argument', opts.forward_args)

    def test_mainline_args_help_default(self):
        with redirect_stdout() as stream:
            main([
                '--help',
            ])
            entries = stream.getvalue()
            self.assertIn('releng-tool <options>', entries)

    def test_mainline_args_help_quirks(self):
        with redirect_stdout() as stream:
            main([
                '--help-quirks',
            ])
            entries = stream.getvalue()
            self.assertIn('releng-tool quirks', entries)

    def test_mainline_args_images_dir_missing(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--images-dir',
            ])

    def test_mainline_args_images_dir_valid(self):
        with self._setup() as engine:
            main([
                '--images-dir',
                'example-path',
            ])
            opts = engine.call_args.args[0]
            self.assertIn('example-path', opts.images_dir)

    def test_mainline_args_injected_args(self):
        with self._setup():
            main([
                'MY_CUSTOM_ARG=123',
            ])
            self.assertIn('MY_CUSTOM_ARG', os.environ)
            self.assertEqual(os.environ['MY_CUSTOM_ARG'], '123')

    def test_mainline_args_jobs_invalid_type(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--jobs',
                'some-value',
            ])

    def test_mainline_args_jobs_missing(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--jobs',
            ])

    def test_mainline_args_jobs_valid_positive(self):
        with self._setup() as engine:
            main([
                '--jobs',
                '42',
            ])
            opts = engine.call_args.args[0]
            self.assertEqual(opts.jobs, 42)

    def test_mainline_args_jobs_valid_zero(self):
        with self._setup() as engine:
            main([
                '--jobs',
                '0',
            ])
            opts = engine.call_args.args[0]
            self.assertNotEqual(opts.jobs, 0)  # auto should populate (>=1)

    def test_mainline_args_nocolorout(self):
        with self._setup(), \
                patch('releng_tool.__main__.releng_log_configuration') as lcfg:
            main([
                '--nocolorout',
            ])
            args = lcfg.call_args.kwargs
            self.assertIn('nocolor', args)
            self.assertTrue(args['nocolor'])

    def test_mainline_args_only_mirror(self):
        with self._setup() as engine:
            main([
                '--only-mirror',
            ])
            opts = engine.call_args.args[0]
            self.assertTrue(opts.only_mirror)

    def test_mainline_args_out_dir_missing(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--out-dir',
            ])

    def test_mainline_args_out_dir_valid(self):
        with self._setup() as engine:
            main([
                '--out-dir',
                'example-path',
            ])
            opts = engine.call_args.args[0]
            self.assertIn('example-path', opts.out_dir)

    def test_mainline_args_profile_missing(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--profile',
            ])

    def test_mainline_args_profile_set_multiple(self):
        with self._setup() as engine:
            main([
                '--profile',
                'my-custom-profile1',
                '--profile',
                'my-custom-profile2',
            ])
            opts = engine.call_args.args[0]
            self.assertIn('my-custom-profile1', opts.profiles)
            self.assertIn('my-custom-profile2', opts.profiles)

    def test_mainline_args_profile_set_single(self):
        with self._setup() as engine:
            main([
                '--profile',
                'my-custom-profile',
            ])
            opts = engine.call_args.args[0]
            self.assertIn('my-custom-profile', opts.profiles)

    def test_mainline_args_quirk_missing(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--quirk',
            ])

    def test_mainline_args_quirk_set(self):
        with self._setup() as engine:
            main([
                '--quirk',
                'releng.ignore_failed_extensions',
            ])
            opts = engine.call_args.args[0]
            self.assertIn('releng.ignore_failed_extensions', opts.quirks)

    def test_mainline_args_relaxed_args_not_set(self):
        with self._setup():
            rv = main([
                '--argument-that-does-not-exist',
            ])
            self.assertEqual(rv, 1)

    def test_mainline_args_relaxed_args_set_arg(self):
        with self._setup():
            rv = main([
                '--argument-that-does-not-exist',
                '--relaxed-args',
            ])
            self.assertEqual(rv, 0)

    def test_mainline_args_relaxed_args_set_env(self):
        with self._setup():
            os.environ['RELENG_IGNORE_UNKNOWN_ARGS'] = '1'
            rv = main([
                '--argument-that-does-not-exist',
            ])
            self.assertEqual(rv, 0)

    def test_mainline_args_relaxed_args_set_ignored(self):
        with self._setup():
            rv = main([
                '--argument-that-does-not-exist',
                '--relaxed-args',
                '--werror',
            ])
            self.assertEqual(rv, 1)

    def test_mainline_args_root_dir_missing(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--root-dir',
            ])

    def test_mainline_args_root_dir_valid(self):
        with self._setup() as engine:
            main([
                '--root-dir',
                'example-path',
            ])
            opts = engine.call_args.args[0]
            self.assertIn('example-path', opts.root_dir)

    def test_mainline_args_sbom_format_invalid(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--sbom-format',
                'some-invalid-format',
            ])

    def test_mainline_args_sbom_format_missing(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--sbom-format',
            ])

    def test_mainline_args_sbom_format_valid(self):
        with self._setup() as engine:
            main([
                '--sbom-format',
                'json',
            ])
            opts = engine.call_args.args[0]
            self.assertIn('json', opts.sbom_format)

    def test_mainline_args_success_exit_code_invalid_type(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--success-exit-code',
                'some-value',
            ])

    def test_mainline_args_success_exit_code_invalid_value(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--success-exit-code',
                '-1',
            ])

    def test_mainline_args_success_exit_code_missing(self):
        with self._setup(), self.assertRaises(SystemExit):
            main([
                '--success-exit-code',
            ])

    def test_mainline_args_success_exit_code_original_error(self):
        with self._setup(rv=False):
            rv = main([
                '--success-exit-code',
                '2',
            ])
            self.assertEqual(rv, 1)

    def test_mainline_args_success_exit_code_set(self):
        with self._setup():
            rv = main([
                '--success-exit-code',
                '42',
            ])
            self.assertEqual(rv, 42)

    def test_mainline_args_verbose(self):
        with self._setup() as engine:
            main([
                '--verbose',
            ])
            opts = engine.call_args.args[0]
            self.assertTrue(opts.verbose)

    def test_mainline_args_werror(self):
        with self._setup(), \
                patch('releng_tool.__main__.releng_log_configuration') as lcfg:
            main([
                '--werror',
            ])
            args = lcfg.call_args.kwargs
            self.assertIn('werror', args)
            self.assertTrue(args['werror'])

    @contextmanager
    def _setup(self, *, rv: bool = True):
        with patch('releng_tool.__main__.RelengEngine') as engine, \
                patch('releng_tool.__main__.releng_log_configuration'):
            engine.return_value.run.return_value = rv
            yield engine
