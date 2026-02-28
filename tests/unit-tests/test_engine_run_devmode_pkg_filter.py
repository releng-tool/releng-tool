# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from contextlib import contextmanager
from pathlib import Path
from releng_tool.defs import Rpk
from releng_tool.packages.pipeline import PipelineResult
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
from unittest.mock import patch
import json


class TestEngineRunDevModePkgFilter(RelengToolTestCase):
    def test_engine_run_devmode_pkgfilter_pkg_enabled_flag(self):
        expected_pkgs = {
            'liba',
            'libb',
            'libc',
        }

        with self._setup(expected_pkgs) as engine:
            # force enable development mode
            Path(engine.opts.ff_devmode).touch()

            setpkgcfg(engine, 'libb', Rpk.DEVMODE_REVISION, value='main')
            setpkgcfg(engine, 'libb', Rpk.ONLY_DEVMODE, value=True)

    def test_engine_run_devmode_pkgfilter_pkg_enabled_mode_multiple(self):
        expected_pkgs = {
            'liba',
            'libb',
            'libc',
        }

        with self._setup(expected_pkgs) as engine:
            # force enable development mode
            with open(engine.opts.ff_devmode, 'w') as f:
                json.dump({
                    'mode': 'example',
                }, f)

            setpkgcfg(engine, 'libb', Rpk.DEVMODE_REVISION, value='main')
            setpkgcfg(engine, 'libb', Rpk.ONLY_DEVMODE, value=[
                'test',
                'example',
                'second',
            ])

    def test_engine_run_devmode_pkgfilter_pkg_enabled_mode_single(self):
        expected_pkgs = {
            'liba',
            'libb',
            'libc',
        }

        with self._setup(expected_pkgs) as engine:
            # force enable development mode
            with open(engine.opts.ff_devmode, 'w') as f:
                json.dump({
                    'mode': 'example',
                }, f)

            setpkgcfg(engine, 'libb', Rpk.DEVMODE_REVISION, value='main')
            setpkgcfg(engine, 'libb', Rpk.ONLY_DEVMODE, value='example')

    def test_engine_run_devmode_pkgfilter_pkg_hidden_default(self):
        expected_pkgs = {
            'liba',
            'libc',
        }

        with self._setup(expected_pkgs) as engine:
            setpkgcfg(engine, 'libb', Rpk.DEVMODE_REVISION, value='main')
            setpkgcfg(engine, 'libb', Rpk.ONLY_DEVMODE, value=True)

    def test_engine_run_devmode_pkgfilter_pkg_hidden_mode(self):
        expected_pkgs = {
            'liba',
            'libc',
        }

        with self._setup(expected_pkgs) as engine:
            # force enable development mode
            with open(engine.opts.ff_devmode, 'w') as f:
                json.dump({
                    'mode': 'other-mode',
                }, f)

            setpkgcfg(engine, 'libb', Rpk.DEVMODE_REVISION, value='main')
            setpkgcfg(engine, 'libb', Rpk.ONLY_DEVMODE, value='example')

    def test_engine_run_devmode_pkgfilter_sanity_check(self):
        expected_pkgs = {
            'liba',
            'libb',
            'libc',
        }

        with self._setup(expected_pkgs):
            pass

    @contextmanager
    def _setup(self, pkgs):
        pkg_process_call = 'releng_tool.engine.RelengPackagePipeline.process'
        with prepare_testenv(template='devmode-filter') as engine, \
                patch(pkg_process_call) as process:
            process.return_value = PipelineResult.CONTINUE

            yield engine
            engine.run()

            found_pkgs = {args[0][0].name for args in process.call_args_list}
            self.assertEqual(found_pkgs, pkgs)
