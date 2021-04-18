# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from releng_tool.opts import RelengEngineOptions
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.manager import RelengPackageManager
from releng_tool.registry import RelengRegistry
from tests.support.pkg_config_test import TestPkgConfigsBase

class TestPkgConfigsDevmode(TestPkgConfigsBase):
    def test_pkgconfig_devmode_ignore_cache_disabled(self):
        pkg, _, _ = self.LOAD('devmode-ignore-cache-disabled')
        self.assertEqual(pkg.devmode_ignore_cache, False)

    def test_pkgconfig_devmode_ignore_cache_enabled(self):
        pkg, _, _ = self.LOAD('devmode-ignore-cache-enabled')
        self.assertEqual(pkg.devmode_ignore_cache, True)

    def test_pkgconfig_devmode_ignore_cache_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('devmode-ignore-cache-invalid')

    def test_pkgconfig_devmode_ignore_cache_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.devmode_ignore_cache)

    def test_pkgconfig_devmode_revision_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('devmode-revision-invalid-type')

    def test_pkgconfig_devmode_revision_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertFalse(pkg.has_devmode_option)

    def test_pkgconfig_devmode_revision_valid_default(self):
        pkg, _, _ = self.LOAD('devmode-revision-valid')
        self.assertEqual(pkg.revision, 'dummy')
        self.assertEqual(pkg.version, 'dummy')
        self.assertTrue(pkg.has_devmode_option)

    def test_pkgconfig_devmode_revision_valid_enabled(self):
        # force engine options to default packages to internal
        opts = RelengEngineOptions()
        opts.devmode = True

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg, _, _ = self.LOAD('devmode-revision-valid', manager=manager)
        self.assertEqual(pkg.revision, 'my-devmode-revision')
        self.assertEqual(pkg.version, 'my-devmode-revision')
        self.assertTrue(pkg.has_devmode_option)
