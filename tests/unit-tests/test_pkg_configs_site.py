# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.opts import RelengEngineOptions
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.manager import RelengPackageManager
from releng_tool.registry import RelengRegistry
from tests.support.pkg_config_test import TestPkgConfigsBase
import sys


class TestPkgConfigsSite(TestPkgConfigsBase):
    def test_pkgconfig_site_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('site-invalid-type')

    def test_pkgconfig_site_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.site)

    def test_pkgconfig_site_valid_devmode_default(self):
        pkg = self.LOAD('site-valid-devmode').package
        self.assertEqual(pkg.site, 'https://example.org/file.tgz')

    def test_pkgconfig_site_valid_devmode_explicit(self):
        opts = RelengEngineOptions()
        opts.devmode = 'build-a'

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg = self.LOAD('site-valid-devmode', manager=manager).package
        self.assertEqual(pkg.site, 'git@git.example.org:my-group/my-prj.git')

    def test_pkgconfig_site_valid_devmode_fallback(self):
        opts = RelengEngineOptions()
        opts.devmode = 'build-c'

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg = self.LOAD('site-valid-devmode', manager=manager).package
        self.assertEqual(pkg.site, 'https://example.org/file.tgz')

    def test_pkgconfig_site_valid_lazy_posix_file(self):
        if sys.platform == 'win32':
            raise self.skipTest('lazy posix test skipped for win32')

        pkg = self.LOAD('site-valid-lazy-posix-file').package
        self.assertEqual(pkg.site, 'file:///opt/some/file')

    def test_pkgconfig_site_valid_simple(self):
        pkg = self.LOAD('site-valid-simple').package
        self.assertEqual(pkg.site, 'https://example.com/file.tgz')
