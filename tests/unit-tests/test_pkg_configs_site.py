# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.opts import RelengEngineOptions
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.manager import RelengPackageManager
from releng_tool.registry import RelengRegistry
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsSite(TestPkgConfigsBase):
    def test_pkgconfig_site_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('site-invalid-type')

    def test_pkgconfig_site_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.site)

    def test_pkgconfig_site_valid_devmode_default(self):
        pkg, _, _ = self.LOAD('site-valid-devmode')
        self.assertEqual(pkg.site, 'https://example.org/file.tgz')

    def test_pkgconfig_site_valid_devmode_explicit(self):
        opts = RelengEngineOptions()
        opts.devmode = 'build-a'

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg, _, _ = self.LOAD('site-valid-devmode', manager=manager)
        self.assertEqual(pkg.site, 'git@git.example.org:my-group/my-prj.git')

    def test_pkgconfig_site_valid_devmode_fallback(self):
        opts = RelengEngineOptions()
        opts.devmode = 'build-c'

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg, _, _ = self.LOAD('site-valid-devmode', manager=manager)
        self.assertEqual(pkg.site, 'https://example.org/file.tgz')

    def test_pkgconfig_site_valid_simple(self):
        pkg, _, _ = self.LOAD('site-valid-simple')
        self.assertEqual(pkg.site, 'https://example.com/file.tgz')
