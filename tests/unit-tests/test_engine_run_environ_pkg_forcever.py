# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.defs import Rpk
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
import os


class TestEngineRunEnvironPkgForceVersion(RelengToolTestCase):
    def test_engine_run_environ_pkg_force_version_sanity_check_devrev(self):
        with prepare_testenv(template='minimal') as engine:
            self._setup_project(engine)

            # force enable development mode
            Path(engine.opts.ff_devmode).touch()

            engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '4.5.6')

    def test_engine_run_environ_pkg_force_version_sanity_check_stdrev(self):
        with prepare_testenv(template='minimal') as engine:
            self._setup_project(engine)
            engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '1.2.3')

    def test_engine_run_environ_pkg_force_version_override_devrev_env(self):
        os.environ['MINIMAL_FORCE_REVISION'] = '6.7.5'

        with prepare_testenv(template='minimal') as engine:
            self._setup_project(engine)

            # force enable development mode
            Path(engine.opts.ff_devmode).touch()

            engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '6.7.5')

    def test_engine_run_environ_pkg_force_version_override_stdrev_env(self):
        os.environ['MINIMAL_FORCE_REVISION'] = '6.7.3'

        with prepare_testenv(template='minimal') as engine:
            self._setup_project(engine)
            engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '6.7.3')

    def test_engine_run_environ_pkg_force_version_override_devrev_inject(self):
        cfg = {
            'injected_kv': {
                'MINIMAL_FORCE_REVISION': '7.8.9',
            },
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            self._setup_project(engine)

            # force enable development mode
            Path(engine.opts.ff_devmode).touch()

            engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '7.8.9')

    def test_engine_run_environ_pkg_force_version_override_stdrev_inject(self):
        cfg = {
            'injected_kv': {
                'MINIMAL_FORCE_REVISION': '7.8.9',
            },
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            self._setup_project(engine)
            engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '7.8.9')

    def test_engine_run_environ_pkg_force_version_release_no_override(self):
        os.environ['MINIMAL_FORCE_REVISION'] = '2.3.6'

        cfg = {
            'release': True,
        }

        with prepare_testenv(config=cfg, template='minimal') as engine:
            self._setup_project(engine)
            engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '1.2.3')

    def _setup_project(self, engine):
        setpkgcfg(engine, 'minimal', Rpk.DEVMODE_REVISION, '4.5.6')
        setpkgcfg(engine, 'minimal', Rpk.REVISION, '1.2.3')
