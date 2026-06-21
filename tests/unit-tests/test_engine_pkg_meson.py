# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PkgAction
from releng_tool.defs import Rpk
from releng_tool.tool.meson import MESON
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
from tests import setprjcfg
from unittest.mock import patch


class TestEnginePkgMeson(RelengToolTestCase):
    @patch('releng_tool.engine.meson.configure.MESON')
    @patch.object(MESON, 'exists', return_value=True)
    def test_engine_pkg_meson_build_type_cfg(self, cmake_exists, meson_cfg):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setprjcfg(engine, 'default_meson_build_type', 'minsize')
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'meson')

            rv = engine.run()
            self.assertTrue(rv)

            meson_cfg.execute.assert_called_once()

            # verify we have provided our minsize build type in the options
            args = meson_cfg.execute.call_args.args[0]
            self.assertIn('--buildtype', args)
            self.assertIn('minsize', args)

    @patch('releng_tool.engine.meson.configure.MESON')
    @patch.object(MESON, 'exists', return_value=True)
    def test_engine_pkg_meson_build_type_default(self, cmake_exists, meson_cfg):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'meson')
            setpkgcfg(engine, 'minimal', Rpk.MESON_BUILD_TYPE, 'minsize')

            rv = engine.run()
            self.assertTrue(rv)

            meson_cfg.execute.assert_called_once()

            # verify we have provided our minsize build type in the options
            args = meson_cfg.execute.call_args.args[0]
            self.assertIn('--buildtype', args)
            self.assertIn('minsize', args)

    @patch('releng_tool.engine.meson.install.MESON')
    @patch('releng_tool.engine.meson.build.MESON')
    @patch('releng_tool.engine.meson.configure.MESON')
    @patch.object(MESON, 'exists', return_value=True)
    def test_engine_pkg_meson_default(self,
            meson_exists, meson_cfg, meson_build, meson_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'meson')

            rv = engine.run()
            self.assertTrue(rv)

            meson_cfg.execute.assert_called_once()
            meson_build.execute.assert_called_once()
            meson_install.execute.assert_called_once()

            # verify the setup argument was provided
            args = meson_cfg.execute.call_args.args[0]
            self.assertIn('setup', args)

            # verify the compile argument was provided
            args = meson_build.execute.call_args.args[0]
            self.assertIn('compile', args)

            # verify the install argument and no-rebuild flag was provided
            args = meson_install.execute.call_args.args[0]
            self.assertIn('install', args)
            self.assertIn('--no-rebuild', args)

            # verify the install call provided an install target
            self.assertEqual(args.count('--destdir'), 1)

            # ensure directory path is provided with the destination directory
            destdir_arg_idx = args.index('--destdir')
            destdir_path_idx = destdir_arg_idx + 1
            self.assertLessEqual(destdir_path_idx, len(args))
            destdir_path = args[destdir_path_idx]
            self.assertFalse(destdir_path.startswith('-'))

            # verify that DESTDIR was set in the install stage
            env_arg = meson_install.execute.call_args.kwargs.get('env')
            self.assertIn('DESTDIR', env_arg)

    @patch('releng_tool.engine.meson.install.MESON')
    @patch('releng_tool.engine.meson.build.MESON')
    @patch('releng_tool.engine.meson.configure.MESON')
    @patch.object(MESON, 'exists', return_value=True)
    def test_engine_pkg_meson_install_staging_and_target(self,
            meson_exists, meson_cfg, meson_build, meson_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.INSTALL_TYPE, 'staging_and_target')
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'meson')

            rv = engine.run()
            self.assertTrue(rv)

            meson_cfg.execute.assert_called_once()
            meson_build.execute.assert_called_once()
            self.assertEqual(meson_install.execute.call_count, 2)

            # verify the install call provided an install target
            meson_install_first = meson_install.execute.call_args_list[0]
            args = meson_install_first.args[0]
            self.assertEqual(args.count('--destdir'), 1)

            # ensure directory path is provided with the destination directory
            destdir_arg_idx = args.index('--destdir')
            destdir_path_idx = destdir_arg_idx + 1
            self.assertLessEqual(destdir_path_idx, len(args))
            destdir_path = args[destdir_path_idx]
            self.assertFalse(destdir_path.startswith('-'))

            # verify that DESTDIR was set in the install stage
            env_arg = meson_install.execute.call_args.kwargs.get('env')
            self.assertIn('DESTDIR', env_arg)

            # verify the install call provided an install target
            meson_install_second = meson_install.execute.call_args_list[1]
            args = meson_install_second.args[0]
            self.assertEqual(args.count('--destdir'), 1)

            # ensure directory path is provided with the destination directory
            destdir_arg_idx = args.index('--destdir')
            destdir_path_idx = destdir_arg_idx + 1
            self.assertLessEqual(destdir_path_idx, len(args))
            destdir_path = args[destdir_path_idx]
            self.assertFalse(destdir_path.startswith('-'))

            # verify that DESTDIR was set in the install stage
            env_arg = meson_install.execute.call_args.kwargs.get('env')
            self.assertIn('DESTDIR', env_arg)

    @patch('releng_tool.engine.meson.configure.MESON')
    @patch.object(MESON, 'exists', return_value=False)
    def test_engine_pkg_meson_missing(self, meson_exists, meson_cfg):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'meson')

            rv = engine.run()
            self.assertFalse(rv)

            meson_cfg.execute.assert_not_called()

    @patch('releng_tool.engine.meson.install.MESON')
    @patch('releng_tool.engine.meson.build.MESON')
    @patch('releng_tool.engine.meson.configure.MESON')
    @patch.object(MESON, 'exists', return_value=True)
    def test_engine_pkg_meson_no_install(self,
            meson_exists, meson_cfg, meson_build, meson_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'meson')
            setpkgcfg(engine, 'minimal', Rpk.MESON_NOINSTALL, value=True)

            rv = engine.run()
            self.assertTrue(rv)

            meson_cfg.execute.assert_called_once()
            meson_build.execute.assert_called_once()
            meson_install.execute.assert_not_called()
