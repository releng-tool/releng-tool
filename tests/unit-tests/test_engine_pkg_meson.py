# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.tool.meson import MESON
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
from unittest.mock import patch


class TestEnginePkgCmake(RelengToolTestCase):
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
