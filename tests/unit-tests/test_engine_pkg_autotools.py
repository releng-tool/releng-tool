# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PkgAction
from releng_tool.defs import Rpk
from releng_tool.tool.autoreconf import AUTORECONF
from releng_tool.tool.make import MAKE
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
from unittest.mock import patch


class TestEnginePkgAutotools(RelengToolTestCase):
    @patch('releng_tool.engine.autotools.configure.execute')
    @patch('releng_tool.engine.autotools.configure.AUTORECONF')
    @patch.object(MAKE, 'exists', return_value=True)
    @patch.object(AUTORECONF, 'exists', return_value=True)
    def test_engine_pkg_autotools_autoreconf_invoke(self,
            autoreconf_exists, make_exists, autoreconf, at_cfg):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'autotools')
            setpkgcfg(engine, 'minimal', Rpk.AUTOTOOLS_AUTORECONF, value=True)

            rv = engine.run()
            self.assertTrue(rv)

            autoreconf.execute.assert_called_once()
            at_cfg.assert_called_once()

    @patch('releng_tool.engine.autotools.configure.AUTORECONF')
    @patch.object(AUTORECONF, 'exists', return_value=False)
    def test_engine_pkg_autotools_autoreconf_missing(self,
            autoreconf_exists, autoreconf):
        cfg = {
            'action': f'minimal-{PkgAction.CONFIGURE}',
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'autotools')
            setpkgcfg(engine, 'minimal', Rpk.AUTOTOOLS_AUTORECONF, value=True)

            rv = engine.run()
            self.assertFalse(rv)

            autoreconf.execute.assert_not_called()

    @patch('releng_tool.engine.autotools.install.MAKE')
    @patch('releng_tool.engine.autotools.build.MAKE')
    @patch('releng_tool.engine.autotools.configure.execute')
    @patch('releng_tool.engine.autotools.configure.AUTORECONF')
    @patch.object(MAKE, 'exists', return_value=True)
    @patch.object(AUTORECONF, 'exists', return_value=True)
    def test_engine_pkg_autotools_default(self,
            autoreconf_exists, make_exists,
            autoreconf, at_cfg, at_build, at_install):
        with prepare_testenv(template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.TYPE, 'autotools')

            rv = engine.run()
            self.assertTrue(rv)

            autoreconf.execute.assert_not_called()
            at_cfg.assert_called_once()
            at_build.execute.assert_called_once()
            at_install.execute.assert_called_once()

            # verify we have provided our cache of options
            args = at_cfg.call_args.args[0]
            self.assertIn('./configure', args)

            # verify the install target was provided
            args = at_install.execute.call_args.args[0]
            self.assertIn('install', args)
