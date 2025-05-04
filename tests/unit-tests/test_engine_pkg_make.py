# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PkgAction
from releng_tool.defs import Rpk
from releng_tool.tool.make import MAKE
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
from unittest.mock import patch


class TestEnginePkgMake(RelengToolTestCase):
    @patch('releng_tool.engine.make.install.MAKE')
    @patch('releng_tool.engine.make.build.MAKE')
    @patch('releng_tool.engine.make.configure.MAKE')
    @patch.object(MAKE, 'exists', return_value=True)
    def test_engine_pkg_make_config_defs(self,
            make_exists, make_cfg, make_build, make_install):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'make')
            setpkgcfg(engine, 'minimal', Rpk.CONF_DEFS, {
                'OPTION': 'VALUE',
            })

            rv = engine.run()
            self.assertTrue(rv)

            make_cfg.execute.assert_called_once()
            make_build.execute.assert_not_called()
            make_install.execute.assert_not_called()

    @patch('releng_tool.engine.make.install.MAKE')
    @patch('releng_tool.engine.make.build.MAKE')
    @patch('releng_tool.engine.make.configure.MAKE')
    @patch.object(MAKE, 'exists', return_value=True)
    def test_engine_pkg_make_config_env(self,
            make_exists, make_cfg, make_build, make_install):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'make')
            setpkgcfg(engine, 'minimal', Rpk.CONF_DEFS, {
                'OPTION': 'VALUE',
            })

            rv = engine.run()
            self.assertTrue(rv)

            make_cfg.execute.assert_called_once()
            make_build.execute.assert_not_called()
            make_install.execute.assert_not_called()

    @patch('releng_tool.engine.make.install.MAKE')
    @patch('releng_tool.engine.make.build.MAKE')
    @patch('releng_tool.engine.make.configure.MAKE')
    @patch.object(MAKE, 'exists', return_value=True)
    def test_engine_pkg_make_config_opts(self,
            make_exists, make_cfg, make_build, make_install):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'make')
            setpkgcfg(engine, 'minimal', Rpk.CONF_OPTS, {
                'OPTION': 'VALUE',
            })

            rv = engine.run()
            self.assertTrue(rv)

            make_cfg.execute.assert_called_once()
            make_build.execute.assert_not_called()
            make_install.execute.assert_not_called()

    @patch('releng_tool.engine.make.install.MAKE')
    @patch('releng_tool.engine.make.build.MAKE')
    @patch('releng_tool.engine.make.configure.MAKE')
    @patch.object(MAKE, 'exists', return_value=True)
    def test_engine_pkg_make_default(self,
            make_exists, make_cfg, make_build, make_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'make')

            rv = engine.run()
            self.assertTrue(rv)

            make_cfg.execute.assert_not_called()
            make_build.execute.assert_called_once()
            make_install.execute.assert_called_once()

            # verify the install target was provided
            args = make_install.execute.call_args.args[0]
            self.assertIn('install', args)

    @patch('releng_tool.engine.make.build.MAKE')
    @patch.object(MAKE, 'exists', return_value=False)
    def test_engine_pkg_make_missing(self, make_exists, make_build):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'make')

            rv = engine.run()
            self.assertFalse(rv)

            make_build.execute.assert_not_called()

    @patch('releng_tool.engine.make.install.MAKE')
    @patch('releng_tool.engine.make.build.MAKE')
    @patch('releng_tool.engine.make.configure.MAKE')
    @patch.object(MAKE, 'exists', return_value=True)
    def test_engine_pkg_make_no_install(self,
            make_exists, make_cfg, make_build, make_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'make')
            setpkgcfg(engine, 'minimal', Rpk.MAKE_NOINSTALL, value=True)

            rv = engine.run()
            self.assertTrue(rv)

            make_cfg.execute.assert_not_called()
            make_build.execute.assert_called_once()
            make_install.execute.assert_not_called()
