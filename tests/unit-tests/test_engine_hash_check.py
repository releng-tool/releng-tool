# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from contextlib import contextmanager
from pathlib import Path
from releng_tool.defs import Rpk
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
from tests.support import fetch_unittest_assets_dir
from unittest.mock import patch
import os
import shutil


class TestEngineHashCheck(RelengToolTestCase):
    def test_engine_hash_check_fail_bad_hash(self):
        with self._setup_engine() as engine:
            self._override_hash(engine, 'bad-hash')
            rv = engine.run()
            # fail if a hash entry is mismatched
            self.assertFalse(rv)

    def test_engine_hash_check_fail_missing(self):
        with self._setup_engine() as engine:
            self._override_filename(engine, 'unknown')
            rv = engine.run()
            # fail if a hash entry is missing
            self.assertFalse(rv)

    def test_engine_hash_check_sic_not_devmode_pkg(self):
        with self._setup_engine() as engine:
            # force enable development mode
            Path(engine.opts.ff_devmode).touch()

            self._override_hash(engine, 'bad-hash')
            setpkgcfg(engine, 'minimal',
                Rpk.DEVMODE_SKIP_INTEGRITY_CHECK, value=True)
            rv = engine.run()
            # fail if DEVMODE_SKIP_INTEGRITY_CHECK is set, even if running
            # in development mode since the package does not have a development
            # revision to target
            self.assertFalse(rv)

    def test_engine_hash_check_sic_not_in_devmode(self):
        with self._setup_engine() as engine:
            self._override_hash(engine, 'bad-hash')
            setpkgcfg(engine, 'minimal',
                Rpk.DEVMODE_SKIP_INTEGRITY_CHECK, value=True)
            rv = engine.run()
            # fail if DEVMODE_SKIP_INTEGRITY_CHECK is set but not in a
            # development mode
            self.assertFalse(rv)

    def test_engine_hash_check_sic_valid(self):
        with self._setup_engine() as engine:
            # force enable development mode
            Path(engine.opts.ff_devmode).touch()

            self._override_hash(engine, 'bad-hash')
            self._override_filename(engine, 'minimal-dummy')
            setpkgcfg(engine, 'minimal', Rpk.DEVMODE_REVISION, value='dummy')
            setpkgcfg(engine, 'minimal',
                Rpk.DEVMODE_SKIP_INTEGRITY_CHECK, value=True)
            rv = engine.run()
            # pass if DEVMODE_SKIP_INTEGRITY_CHECK is set, we are in
            # development mode and we have a development revision
            self.assertTrue(rv)

    def test_engine_hash_check_valid(self):
        with self._setup_engine() as engine:
            rv = engine.run()
            # default file with sane hash should pass
            self.assertTrue(rv)

    @contextmanager
    def _setup_engine(self, cfg=None):
        dummy_site = 'http://www.example.com/test.tgz'

        assets = fetch_unittest_assets_dir('sample-files')
        archive = os.path.join(assets, 'sample-files.tgz')
        archive_hash = os.path.join(assets, 'sample-files.tgz.hash')

        with prepare_testenv(config=cfg, template='minimal') as engine:
            setpkgcfg(engine, 'minimal', Rpk.SITE, value=dummy_site)
            setpkgcfg(engine, 'minimal', Rpk.VERSION, value=None)

            # setup valid hash configuration
            root_dir = Path(engine.opts.root_dir)
            pkg_hash = root_dir / 'package' / 'minimal' / 'minimal.hash'
            shutil.copy(archive_hash, pkg_hash)
            content = pkg_hash.read_text()
            new_content = content.replace('sample-files', 'minimal')
            pkg_hash.write_text(new_content)

            # mock the fetch operation to copy over the test artifact into
            # the expected cache file
            def mocked_fetch(opts):
                cache_file = opts.cache_file
                shutil.copy(archive, cache_file)
                return cache_file

            with patch('releng_tool.engine.fetch.fetch_url', mocked_fetch):
                yield engine

    def _override_filename(self, engine, new_filename):
        root_dir = Path(engine.opts.root_dir)
        pkg_hash = root_dir / 'package' / 'minimal' / 'minimal.hash'
        content = pkg_hash.read_text()
        new_content = content.replace('minimal', new_filename)
        pkg_hash.write_text(new_content)

    def _override_hash(self, engine, new_hash):
        root_dir = Path(engine.opts.root_dir)
        pkg_hash = root_dir / 'package' / 'minimal' / 'minimal.hash'
        pkg_hash.write_text(f'sha1 {new_hash} minimal.tgz')
