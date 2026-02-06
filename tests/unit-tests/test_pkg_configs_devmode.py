# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.opts import RelengEngineOptions
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.manager import RelengPackageManager
from releng_tool.registry import RelengRegistry
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsDevmode(TestPkgConfigsBase):
    def test_pkgconfig_devmode_ignore_cache_disabled(self):
        pkg = self.LOAD('devmode-ignore-cache-disabled').package
        self.assertEqual(pkg.devmode_ignore_cache, False)

    def test_pkgconfig_devmode_ignore_cache_enabled(self):
        pkg = self.LOAD('devmode-ignore-cache-enabled').package
        self.assertEqual(pkg.devmode_ignore_cache, True)

    def test_pkgconfig_devmode_ignore_cache_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('devmode-ignore-cache-invalid')

    def test_pkgconfig_devmode_ignore_cache_default_on(self):
        opts = RelengEngineOptions()
        opts.default_dev_ignore_cache = True

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg = self.LOAD('missing', manager=manager).package
        self.assertTrue(pkg.devmode_ignore_cache)

    def test_pkgconfig_devmode_ignore_cache_default_off(self):
        opts = RelengEngineOptions()
        opts.default_dev_ignore_cache = False

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg = self.LOAD('missing', manager=manager).package
        self.assertFalse(pkg.devmode_ignore_cache)

    def test_pkgconfig_devmode_ignore_cache_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.devmode_ignore_cache)

    def test_pkgconfig_devmode_revision_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('devmode-revision-invalid-type')

    def test_pkgconfig_devmode_revision_missing(self):
        pkg = self.LOAD('missing').package
        self.assertFalse(pkg.devmode)

    def test_pkgconfig_devmode_revision_valid_default(self):
        pkg = self.LOAD('devmode-revision-valid').package
        self.assertEqual(pkg.revision, 'dummy')
        self.assertEqual(pkg.version, 'dummy')
        self.assertFalse(pkg.devmode)

    def test_pkgconfig_devmode_revision_valid_enabled(self):
        opts = RelengEngineOptions()
        opts.devmode = 'custom2'

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg = self.LOAD('devmode-revision-valid', manager=manager).package
        self.assertEqual(pkg.revision, 'my-devmode-revision2')
        self.assertEqual(pkg.version, 'my-devmode-revision2')
        self.assertTrue(pkg.devmode)

    def test_pkgconfig_devmode_revision_valid_enabled_deprecated(self):
        opts = RelengEngineOptions()
        opts.devmode = True

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg = self.LOAD(
            'devmode-revision-valid-deprecated',
            manager=manager).package
        self.assertEqual(pkg.revision, 'my-devmode-revision')
        self.assertEqual(pkg.version, 'my-devmode-revision')
        self.assertTrue(pkg.devmode)

    def test_pkgconfig_devmode_revision_valid_fallback_asterisk_raw(self):
        opts = RelengEngineOptions()
        opts.devmode = 'another-mode'

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg = self.LOAD(
            'devmode-revision-valid-fallback-asterisk-raw',
            manager=manager).package
        self.assertEqual(pkg.revision, 'my-fallback-asterisk-raw')
        self.assertEqual(pkg.version, 'dummy')
        self.assertFalse(pkg.devmode)

    def test_pkgconfig_devmode_revision_valid_fallback_asterisk_var(self):
        opts = RelengEngineOptions()
        opts.devmode = 'some-mode'

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg = self.LOAD(
            'devmode-revision-valid-fallback-asterisk-var',
            manager=manager).package
        self.assertEqual(pkg.revision, 'my-fallback-asterisk-variable')
        self.assertEqual(pkg.version, 'dummy')
        self.assertFalse(pkg.devmode)

    def test_pkgconfig_devmode_revision_valid_fallback_version(self):
        opts = RelengEngineOptions()
        opts.devmode = 'custom4'

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg = self.LOAD(
            'devmode-revision-valid-fallback-version',
            manager=manager).package
        self.assertEqual(pkg.revision, 'dummy')
        self.assertEqual(pkg.version, 'dummy')
        self.assertFalse(pkg.devmode)
