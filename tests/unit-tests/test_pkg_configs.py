# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from releng_tool.defs import PackageInstallType
from releng_tool.opts import RelengEngineOptions
from releng_tool.packages.exceptions import RelengToolConflictingConfiguration
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.exceptions import RelengToolUnknownInstallType
from releng_tool.packages.manager import RelengPackageManager
from releng_tool.registry import RelengRegistry
from tests.support.pkg_config_test import TestPkgConfigsBase

class TestPkgConfigs(TestPkgConfigsBase):
    def test_pkgconfig_deps_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('deps-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('deps-invalid-value')

    def test_pkgconfig_deps_missing(self):
        _, _, deps = self.LOAD('missing')
        self.assertListEqual(deps, [])

    def test_pkgconfig_deps_valid(self):
        _, _, deps = self.LOAD('deps-valid-empty')
        self.assertListEqual(deps, [])

        _, _, deps = self.LOAD('deps-valid-multiple')
        self.assertListEqual(deps, [
            'dep1',
            'dep2',
            'dep3',
        ])

        _, _, deps = self.LOAD('deps-valid-single')
        self.assertListEqual(deps, [
            'dep',
        ])

    def test_pkgconfig_fixed_jobs_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('fixed-jobs-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('fixed-jobs-invalid-value')

    def test_pkgconfig_fixed_jobs_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.fixed_jobs)

    def test_pkgconfig_fixed_jobs_valid(self):
        pkg, _, _ = self.LOAD('fixed-jobs-valid')
        self.assertEqual(pkg.fixed_jobs, 24)

    def test_pkgconfig_install_type_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-type-invalid-type')

        with self.assertRaises(RelengToolUnknownInstallType):
            self.LOAD('install-type-invalid-value')

    def test_pkgconfig_install_type_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.install_type)

    def test_pkgconfig_install_type_valid(self):
        pkg, _, _ = self.LOAD('install-type-valid-host')
        self.assertEqual(pkg.install_type, PackageInstallType.HOST)

        pkg, _, _ = self.LOAD('install-type-valid-images')
        self.assertEqual(pkg.install_type, PackageInstallType.IMAGES)

        pkg, _, _ = self.LOAD('install-type-valid-staging')
        self.assertEqual(pkg.install_type, PackageInstallType.STAGING)

        pkg, _, _ = self.LOAD('install-type-valid-staging-target')
        self.assertEqual(pkg.install_type,
            PackageInstallType.STAGING_AND_TARGET)

        pkg, _, _ = self.LOAD('install-type-valid-target')
        self.assertEqual(pkg.install_type, PackageInstallType.TARGET)

    def test_pkgconfig_is_internal_disabled(self):
        pkg, _, _ = self.LOAD('internal-flag-disabled')
        self.assertFalse(pkg.is_internal)

        pkg, _, _ = self.LOAD('external-flag-disabled')
        self.assertTrue(pkg.is_internal)

        pkg, _, _ = self.LOAD('internal-external-flag-disabled')
        self.assertFalse(pkg.is_internal)

    def test_pkgconfig_is_internal_enabled(self):
        pkg, _, _ = self.LOAD('internal-flag-enabled')
        self.assertTrue(pkg.is_internal)

        pkg, _, _ = self.LOAD('external-flag-enabled')
        self.assertFalse(pkg.is_internal)

        pkg, _, _ = self.LOAD('internal-external-flag-enabled')
        self.assertTrue(pkg.is_internal)

    def test_pkgconfig_is_internal_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('internal-flag-invalid')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('external-flag-invalid')

        with self.assertRaises(RelengToolConflictingConfiguration):
            self.LOAD('internal-external-flag-conflict1')

        with self.assertRaises(RelengToolConflictingConfiguration):
            self.LOAD('internal-external-flag-conflict2')

    def test_pkgconfig_is_internal_missing_default(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertFalse(pkg.is_internal)

    def test_pkgconfig_is_internal_missing_implicit_internal(self):
        # force engine options to default packages to internal
        opts = RelengEngineOptions()
        opts.default_internal_pkgs = True

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg, _, _ = self.LOAD('missing', manager=manager)
        self.assertTrue(pkg.is_internal)

    def test_pkgconfig_license_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('license-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('license-invalid-value')

    def test_pkgconfig_license_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.license)

    def test_pkgconfig_license_valid(self):
        pkg, _, _ = self.LOAD('license-valid-empty')
        self.assertListEqual(pkg.license, [])

        pkg, _, _ = self.LOAD('license-valid-multiple')
        self.assertListEqual(pkg.license, [
            'license1',
            'license2',
            'license3',
        ])

        pkg, _, _ = self.LOAD('license-valid-single')
        self.assertListEqual(pkg.license, [
            'license',
        ])

    def test_pkgconfig_license_files_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('license-files-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('license-files-invalid-value')

    def test_pkgconfig_license_files_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.license_files)

    def test_pkgconfig_license_files_valid(self):
        pkg, _, _ = self.LOAD('license-files-valid-empty')
        self.assertListEqual(pkg.license_files, [])

        pkg, _, _ = self.LOAD('license-files-valid-multiple')
        self.assertListEqual(pkg.license_files, [
            'license-file1',
            'license-file2',
            'license-file3',
        ])

        pkg, _, _ = self.LOAD('license-files-valid-single')
        self.assertListEqual(pkg.license_files, [
            'license-file',
        ])

    def test_pkgconfig_no_extraction_disabled(self):
        pkg, _, _ = self.LOAD('no-extraction-disabled')
        self.assertFalse(pkg.no_extraction)

    def test_pkgconfig_no_extraction_enabled(self):
        pkg, _, _ = self.LOAD('no-extraction-enabled')
        self.assertTrue(pkg.no_extraction)

    def test_pkgconfig_no_extraction_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('no-extraction-invalid')

    def test_pkgconfig_no_extraction_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.no_extraction)

    def test_pkgconfig_prefix_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('prefix-invalid-type')

    def test_pkgconfig_prefix_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.prefix)

    def test_pkgconfig_prefix_valid(self):
        pkg, _, _ = self.LOAD('prefix-valid')
        self.assertEqual(pkg.prefix, 'myprefix')

    def test_pkgconfig_python_interpreter_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('python-interpreter-invalid-type')

    def test_pkgconfig_python_interpreter_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.python_interpreter)

    def test_pkgconfig_python_interpreter_valid(self):
        pkg, _, _ = self.LOAD('python-interpreter-valid')
        self.assertEqual(pkg.python_interpreter, 'mypython')

    def test_pkgconfig_revision_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('revision-invalid-type')

    def test_pkgconfig_revision_valid_explicit(self):
        pkg, _, _ = self.LOAD('revision-valid-explicit')
        self.assertEqual(pkg.revision, 'myrevision')

    def test_pkgconfig_revision_valid_implicit(self):
        pkg, _, _ = self.LOAD('revision-valid-implicit')
        self.assertEqual(pkg.revision, 'myversion')

    def test_pkgconfig_site_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('site-invalid-type')

    def test_pkgconfig_site_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.site)

    def test_pkgconfig_site_valid(self):
        pkg, _, _ = self.LOAD('site-valid')
        self.assertEqual(pkg.site, 'https://example.com/file.tgz')

    def test_pkgconfig_strip_count_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('strip-count-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('strip-count-invalid-value')

    def test_pkgconfig_strip_count_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertEqual(pkg.strip_count, 1) # default

    def test_pkgconfig_strip_count_valid(self):
        pkg, _, _ = self.LOAD('strip-count-valid-zero')
        self.assertEqual(pkg.strip_count, 0)

        pkg, _, _ = self.LOAD('strip-count-valid-nonzero')
        self.assertEqual(pkg.strip_count, 2)
