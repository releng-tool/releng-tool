# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PkgAction
from releng_tool.defs import Rpk
from releng_tool.tool.scons import SCONS
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
from unittest.mock import patch


class TestEnginePkgMake(RelengToolTestCase):
    @patch('releng_tool.engine.scons.install.SCONS')
    @patch('releng_tool.engine.scons.build.SCONS')
    @patch('releng_tool.engine.scons.configure.SCONS')
    @patch.object(SCONS, 'exists', return_value=True)
    def test_engine_pkg_scons_config_defs(self,
            scons_exists, scons_cfg, scons_build, scons_install):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'scons')
            setpkgcfg(engine, 'minimal', Rpk.CONF_DEFS, {
                'OPTION': 'VALUE',
            })

            rv = engine.run()
            self.assertTrue(rv)

            scons_cfg.execute.assert_called_once()
            scons_build.execute.assert_not_called()
            scons_install.execute.assert_not_called()

    @patch('releng_tool.engine.scons.install.SCONS')
    @patch('releng_tool.engine.scons.build.SCONS')
    @patch('releng_tool.engine.scons.configure.SCONS')
    @patch.object(SCONS, 'exists', return_value=True)
    def test_engine_pkg_scons_config_env(self,
            scons_exists, scons_cfg, scons_build, scons_install):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'scons')
            setpkgcfg(engine, 'minimal', Rpk.CONF_DEFS, {
                'OPTION': 'VALUE',
            })

            rv = engine.run()
            self.assertTrue(rv)

            scons_cfg.execute.assert_called_once()
            scons_build.execute.assert_not_called()
            scons_install.execute.assert_not_called()

    @patch('releng_tool.engine.scons.install.SCONS')
    @patch('releng_tool.engine.scons.build.SCONS')
    @patch('releng_tool.engine.scons.configure.SCONS')
    @patch.object(SCONS, 'exists', return_value=True)
    def test_engine_pkg_scons_config_opts(self,
            scons_exists, scons_cfg, scons_build, scons_install):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'scons')
            setpkgcfg(engine, 'minimal', Rpk.CONF_OPTS, {
                'OPTION': 'VALUE',
            })

            rv = engine.run()
            self.assertTrue(rv)

            scons_cfg.execute.assert_called_once()
            scons_build.execute.assert_not_called()
            scons_install.execute.assert_not_called()

    @patch('releng_tool.engine.scons.install.SCONS')
    @patch('releng_tool.engine.scons.build.SCONS')
    @patch('releng_tool.engine.scons.configure.SCONS')
    @patch.object(SCONS, 'exists', return_value=True)
    def test_engine_pkg_scons_default(self,
            scons_exists, scons_cfg, scons_build, scons_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'scons')

            rv = engine.run()
            self.assertTrue(rv)

            scons_cfg.execute.assert_not_called()
            scons_build.execute.assert_called_once()
            scons_install.execute.assert_called_once()

            # verify the install target was provided
            args = scons_install.execute.call_args.args[0]
            self.assertIn('install', args)

    @patch('releng_tool.engine.scons.build.SCONS')
    @patch.object(SCONS, 'exists', return_value=False)
    def test_engine_pkg_scons_missing(self, scons_exists, scons_build):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'scons')

            rv = engine.run()
            self.assertFalse(rv)

            scons_build.execute.assert_not_called()

    @patch('releng_tool.engine.scons.install.SCONS')
    @patch('releng_tool.engine.scons.build.SCONS')
    @patch('releng_tool.engine.scons.configure.SCONS')
    @patch.object(SCONS, 'exists', return_value=True)
    def test_engine_pkg_scons_no_install(self,
            scons_exists, scons_cfg, scons_build, scons_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'scons')
            setpkgcfg(engine, 'minimal', Rpk.SCONS_NOINSTALL, value=True)

            rv = engine.run()
            self.assertTrue(rv)

            scons_cfg.execute.assert_not_called()
            scons_build.execute.assert_called_once()
            scons_install.execute.assert_not_called()
