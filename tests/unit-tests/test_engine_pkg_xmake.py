# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PkgAction
from releng_tool.defs import Rpk
from releng_tool.tool.xmake import XMAKE
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
from tests import setprjcfg
from unittest.mock import patch


class TestEnginePkgXmake(RelengToolTestCase):
    @patch('releng_tool.engine.xmake.configure.XMAKE')
    @patch.object(XMAKE, 'exists', return_value=True)
    def test_engine_pkg_xmake_build_type_cfg(self, xmake_exists, xmake_cfg):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setprjcfg(engine, 'default_xmake_build_type', 'CustomType')
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'xmake')

            rv = engine.run()
            self.assertTrue(rv)

            xmake_cfg.execute.assert_called_once()

            # verify we have provided the mode
            args = xmake_cfg.execute.call_args.args[0]
            expected_arg = '--mode=CustomType'
            has_arg = any(arg.startswith(expected_arg) for arg in args)
            self.assertTrue(has_arg)

    @patch('releng_tool.engine.xmake.configure.XMAKE')
    @patch.object(XMAKE, 'exists', return_value=True)
    def test_engine_pkg_xmake_build_type_default(self, xmake_exists, xmake_cfg):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'xmake')

            rv = engine.run()
            self.assertTrue(rv)

            xmake_cfg.execute.assert_called_once()

            # verify we have no default mode in our config request
            args = xmake_cfg.execute.call_args.args[0]
            self.assertNotIn('--mode', args)

    @patch('releng_tool.engine.xmake.configure.XMAKE')
    @patch.object(XMAKE, 'exists', return_value=True)
    def test_engine_pkg_xmake_build_type_set(self, xmake_exists, xmake_cfg):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'xmake')
            setpkgcfg(engine, 'minimal', Rpk.XMAKE_BUILD_TYPE, 'debug')

            rv = engine.run()
            self.assertTrue(rv)

            xmake_cfg.execute.assert_called_once()

            # verify we have provided the mode
            args = xmake_cfg.execute.call_args.args[0]
            expected_arg = '--mode=debug'
            has_arg = any(arg.startswith(expected_arg) for arg in args)
            self.assertTrue(has_arg)

    @patch('releng_tool.engine.xmake.install.XMAKE')
    @patch('releng_tool.engine.xmake.build.XMAKE')
    @patch('releng_tool.engine.xmake.configure.XMAKE')
    @patch.object(XMAKE, 'exists', return_value=True)
    def test_engine_pkg_xmake_default(self,
            xmake_exists, xmake_cfg, xmake_build, xmake_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'xmake')

            rv = engine.run()
            self.assertTrue(rv)

            xmake_cfg.execute.assert_called_once()
            xmake_build.execute.assert_called_once()
            xmake_install.execute.assert_called_once()

            # verify the config argument was provided
            args = xmake_cfg.execute.call_args.args[0]
            self.assertIn('config', args)

            # verify the config call provided an build target
            self.assertEqual(args.count('-o'), 1)

            # ensure directory path is provided with the build directory
            builddir_arg_idx = args.index('-o')
            builddir_path_idx = builddir_arg_idx + 1
            self.assertLessEqual(builddir_path_idx, len(args))
            builddir_path = args[builddir_path_idx]
            self.assertFalse(builddir_path.startswith('-'))

            # verify that XMAKE_CONFIGDIR was set in the config stage
            env_arg = xmake_install.execute.call_args.kwargs.get('env')
            self.assertIn('XMAKE_CONFIGDIR', env_arg)

            # verify the build argument was provided
            args = xmake_build.execute.call_args.args[0]
            self.assertIn('build', args)

            # verify that XMAKE_CONFIGDIR was set in the build stage
            env_arg = xmake_build.execute.call_args.kwargs.get('env')
            self.assertIn('XMAKE_CONFIGDIR', env_arg)

            # verify the install argument was provided
            args = xmake_install.execute.call_args.args[0]
            self.assertIn('install', args)

            # verify the install call provided an install target
            has_target = any(arg.startswith('--installdir=') for arg in args)
            self.assertTrue(has_target)

            # verify that XMAKE_CONFIGDIR was set in the install stage
            env_arg = xmake_install.execute.call_args.kwargs.get('env')
            self.assertIn('XMAKE_CONFIGDIR', env_arg)

    @patch('releng_tool.engine.xmake.configure.XMAKE')
    @patch.object(XMAKE, 'exists', return_value=False)
    def test_engine_pkg_xmake_missing(self, xmake_exists, xmake_cfg):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'xmake')

            rv = engine.run()
            self.assertFalse(rv)

            xmake_cfg.execute.assert_not_called()

    @patch('releng_tool.engine.xmake.install.XMAKE')
    @patch('releng_tool.engine.xmake.build.XMAKE')
    @patch('releng_tool.engine.xmake.configure.XMAKE')
    @patch.object(XMAKE, 'exists', return_value=True)
    def test_engine_pkg_xmake_no_install(self,
            xmake_exists, xmake_cfg, xmake_build, xmake_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'xmake')
            setpkgcfg(engine, 'minimal', Rpk.XMAKE_NOINSTALL, value=True)

            rv = engine.run()
            self.assertTrue(rv)

            xmake_cfg.execute.assert_called_once()
            xmake_build.execute.assert_called_once()
            xmake_install.execute.assert_not_called()
