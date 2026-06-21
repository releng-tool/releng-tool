# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.tool.waf import WAF
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
from unittest.mock import patch


class TestEnginePkgWaf(RelengToolTestCase):
    @patch('releng_tool.engine.waf.install.WAF')
    @patch('releng_tool.engine.waf.build.WAF')
    @patch('releng_tool.engine.waf.configure.WAF')
    @patch.object(WAF, 'exists', return_value=True)
    def test_engine_pkg_waf_default(self,
            waf_exists, waf_cfg, waf_build, waf_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'waf')

            rv = engine.run()
            self.assertTrue(rv)

            waf_cfg.execute.assert_called_once()
            waf_build.execute.assert_called_once()
            waf_install.execute.assert_called_once()

            # verify the configure argument was provided
            args = waf_cfg.execute.call_args.args[0]
            self.assertIn('configure', args)

            # verify the config call provided a output target
            has_target = any(arg.startswith('--out=') for arg in args)
            self.assertTrue(has_target)

            # verify the build argument was provided
            args = waf_build.execute.call_args.args[0]
            self.assertIn('build', args)

            # verify the install argument was provided
            args = waf_install.execute.call_args.args[0]
            self.assertIn('install', args)

            # verify the install call provided an install target
            self.assertEqual(args.count('--destdir'), 1)

            # ensure directory path is provided with the destination directory
            destdir_arg_idx = args.index('--destdir')
            destdir_path_idx = destdir_arg_idx + 1
            self.assertLessEqual(destdir_path_idx, len(args))
            destdir_path = args[destdir_path_idx]
            self.assertFalse(destdir_path.startswith('-'))

            # verify that DESTDIR was set in the install stage
            env_arg = waf_install.execute.call_args.kwargs.get('env')
            self.assertIn('DESTDIR', env_arg)

    @patch('releng_tool.engine.waf.install.WAF')
    @patch('releng_tool.engine.waf.build.WAF')
    @patch('releng_tool.engine.waf.configure.WAF')
    @patch.object(WAF, 'exists', return_value=True)
    def test_engine_pkg_waf_install_staging_and_target(self,
            waf_exists, waf_cfg, waf_build, waf_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.INSTALL_TYPE, 'staging_and_target')
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'waf')

            rv = engine.run()
            self.assertTrue(rv)

            waf_cfg.execute.assert_called_once()
            waf_build.execute.assert_called_once()
            self.assertEqual(waf_install.execute.call_count, 2)

            # verify the install call provided an install target
            waf_install_first = waf_install.execute.call_args_list[0]
            args = waf_install_first.args[0]
            self.assertEqual(args.count('--destdir'), 1)

            # ensure directory path is provided with the destination directory
            destdir_arg_idx = args.index('--destdir')
            destdir_path_idx = destdir_arg_idx + 1
            self.assertLessEqual(destdir_path_idx, len(args))
            destdir_path = args[destdir_path_idx]
            self.assertFalse(destdir_path.startswith('-'))

            # verify that DESTDIR was set in the install stage
            env_arg = waf_install.execute.call_args.kwargs.get('env')
            self.assertIn('DESTDIR', env_arg)

            # verify the install call provided an install target
            waf_install_second = waf_install.execute.call_args_list[1]
            args = waf_install_second.args[0]
            self.assertEqual(args.count('--destdir'), 1)

            # ensure directory path is provided with the destination directory
            destdir_arg_idx = args.index('--destdir')
            destdir_path_idx = destdir_arg_idx + 1
            self.assertLessEqual(destdir_path_idx, len(args))
            destdir_path = args[destdir_path_idx]
            self.assertFalse(destdir_path.startswith('-'))

            # verify that DESTDIR was set in the install stage
            env_arg = waf_install.execute.call_args.kwargs.get('env')
            self.assertIn('DESTDIR', env_arg)

    @patch('releng_tool.engine.waf.configure.WAF')
    @patch.object(WAF, 'exists', return_value=False)
    def test_engine_pkg_waf_missing(self, waf_exists, waf_cfg):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'waf')

            rv = engine.run()
            self.assertFalse(rv)

            waf_cfg.execute.assert_not_called()

    @patch('releng_tool.engine.waf.install.WAF')
    @patch('releng_tool.engine.waf.build.WAF')
    @patch('releng_tool.engine.waf.configure.WAF')
    @patch.object(WAF, 'exists', return_value=True)
    def test_engine_pkg_waf_no_install(self,
            waf_exists, waf_cfg, waf_build, waf_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'waf')
            setpkgcfg(engine, 'minimal', Rpk.WAF_NOINSTALL, value=True)

            rv = engine.run()
            self.assertTrue(rv)

            waf_cfg.execute.assert_called_once()
            waf_build.execute.assert_called_once()
            waf_install.execute.assert_not_called()
