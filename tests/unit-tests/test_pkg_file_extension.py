# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from tests import RelengToolTestCase
from tests import prepare_testenv


class TestPkgFileExtension(RelengToolTestCase):
    def test_pkg_file_extension_default(self):
        with prepare_testenv(template='pkg-extension') as engine:
            pkg = engine.pkgman.load(['default'])[0]
            suffix = Path(pkg.cache_file).suffix
            self.assertEqual(suffix, '.default')

    def test_pkg_file_extension_less(self):
        with prepare_testenv(template='pkg-extension') as engine:
            pkg = engine.pkgman.load(['extensionless'])[0]
            suffix = Path(pkg.cache_file).suffix
            self.assertEqual(suffix, '')

    def test_pkg_file_extension_set(self):
        with prepare_testenv(template='pkg-extension') as engine:
            pkg = engine.pkgman.load(['extension'])[0]
            suffix = Path(pkg.cache_file).suffix
            self.assertEqual(suffix, '.custom')
