# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.defs import PkgAction
from releng_tool.defs import Rpk
from releng_tool.tool.cmake import CMAKE
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
from unittest.mock import patch
import os


class TestEnginePkgCmake(RelengToolTestCase):
    @patch('releng_tool.engine.cmake.configure.CMAKE')
    @patch.object(CMAKE, 'exists', return_value=True)
    def test_engine_pkg_cmake_build_type(self, cmake_exists, cmake_cfg):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'cmake')
            setpkgcfg(engine, 'minimal', Rpk.CMAKE_BUILD_TYPE, 'Debug')

            rv = engine.run()
            self.assertTrue(rv)

            cmake_cfg.execute.assert_called_once()

            # verify we have provided our cache of options
            args = cmake_cfg.execute.call_args.args[0]
            self.assertIn('-C', args)

            # ensure the cache file exists and is sane
            cache_arg_idx = args.index('-C')
            cache_file_idx = cache_arg_idx + 1
            self.assertLessEqual(cache_file_idx, len(args))
            cache_file = Path(args[cache_file_idx])
            self.assertTrue(cache_file.is_file())

            lines = cache_file.read_text().splitlines()
            self.assertIn('set('
                'CMAKE_BUILD_TYPE "Debug" '
                'CACHE INTERNAL "releng-tool generated")',
                lines)

    @patch('releng_tool.engine.cmake.install.CMAKE')
    @patch('releng_tool.engine.cmake.build.CMAKE')
    @patch('releng_tool.engine.cmake.configure.CMAKE')
    @patch.object(CMAKE, 'exists', return_value=True)
    def test_engine_pkg_cmake_default(self,
            cmake_exists, cmake_cfg, cmake_build, cmake_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'cmake')

            rv = engine.run()
            self.assertTrue(rv)

            cmake_cfg.execute.assert_called_once()
            cmake_build.execute.assert_called_once()
            cmake_install.execute.assert_called_once()

            # verify we have provided our cache of options
            args = cmake_cfg.execute.call_args.args[0]
            self.assertIn('-C', args)

            # ensure the cache file exists and is sane
            cache_arg_idx = args.index('-C')
            cache_file_idx = cache_arg_idx + 1
            self.assertLessEqual(cache_file_idx, len(args))
            cache_file = Path(args[cache_file_idx])
            self.assertTrue(cache_file.is_file())

            lines = cache_file.read_text().splitlines()
            self.assertIn('set('
                'CMAKE_BUILD_TYPE "RelWithDebInfo" '
                'CACHE INTERNAL "releng-tool generated")',
                lines)

            # ensure we target the build directory when populating the
            # configuration
            build_dir = os.environ['MINIMAL_BUILD_DIR']
            self.assertIn(build_dir, args)

            # verify the build argument was provided
            args = cmake_build.execute.call_args.args[0]
            self.assertIn('--build', args)

            # verify the install target was provided
            args = cmake_install.execute.call_args.args[0]
            self.assertIn('--target', args)

            cache_arg_idx = args.index('--target')
            cache_target_idx = cache_arg_idx + 1
            self.assertLessEqual(cache_target_idx, len(args))
            target_arg = args[cache_target_idx]
            self.assertTrue(target_arg, 'install')

    @patch('releng_tool.engine.cmake.configure.CMAKE')
    @patch.object(CMAKE, 'exists', return_value=False)
    def test_engine_pkg_cmake_missing(self, cmake_exists, cmake_cfg):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'cmake')

            rv = engine.run()
            self.assertFalse(rv)

            cmake_cfg.execute.assert_not_called()

    @patch('releng_tool.engine.cmake.install.CMAKE')
    @patch('releng_tool.engine.cmake.build.CMAKE')
    @patch('releng_tool.engine.cmake.configure.CMAKE')
    @patch.object(CMAKE, 'exists', return_value=True)
    def test_engine_pkg_cmake_no_install(self,
            cmake_exists, cmake_cfg, cmake_build, cmake_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'cmake')
            setpkgcfg(engine, 'minimal', Rpk.CMAKE_NOINSTALL, value=True)

            rv = engine.run()
            self.assertTrue(rv)

            cmake_cfg.execute.assert_called_once()
            cmake_build.execute.assert_called_once()
            cmake_install.execute.assert_not_called()
