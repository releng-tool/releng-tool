# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PackageInstallType
from releng_tool.defs import VOID
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
        deps = self.LOAD('missing').dependencies
        self.assertListEqual(deps, [])

    def test_pkgconfig_deps_valid(self):
        deps = self.LOAD('deps-valid-empty').dependencies
        self.assertListEqual(deps, [])

        deps = self.LOAD('deps-valid-multiple').dependencies
        self.assertListEqual(deps, [
            'dep1',
            'dep2',
            'dep3',
        ])

        deps = self.LOAD('deps-valid-single').dependencies
        self.assertListEqual(deps, [
            'dep',
        ])

    def test_pkgconfig_fetch_opts_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('fetch-opts-invalid-base-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('fetch-opts-invalid-key-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('fetch-opts-invalid-value-type')

    def test_pkgconfig_fetch_opts_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.fetch_opts)

    def test_pkgconfig_fetch_opts_valid(self):
        pkg = self.LOAD('fetch-opts-valid-dict').package
        self.assertDictEqual(pkg.fetch_opts, {
            'key1': None,
            'key4': 'value',
            'key8': None,
            'key3': 'val3',
        })

        pkg = self.LOAD('fetch-opts-valid-str').package
        self.assertDictEqual(pkg.fetch_opts, {
            '--my-option': VOID,
        })

        pkg = self.LOAD('fetch-opts-valid-strs').package
        self.assertDictEqual(pkg.fetch_opts, {
            'option4': VOID,
            'option5': VOID,
            'option6': VOID,
        })

    def test_pkgconfig_fixed_jobs_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('fixed-jobs-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('fixed-jobs-invalid-value')

    def test_pkgconfig_fixed_jobs_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.fixed_jobs)

    def test_pkgconfig_fixed_jobs_valid(self):
        pkg = self.LOAD('fixed-jobs-valid').package
        self.assertEqual(pkg.fixed_jobs, 24)

    def test_pkgconfig_install_type_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-type-invalid-type')

        with self.assertRaises(RelengToolUnknownInstallType):
            self.LOAD('install-type-invalid-value')

    def test_pkgconfig_install_type_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.install_type)

    def test_pkgconfig_install_type_valid(self):
        pkg = self.LOAD('install-type-valid-host').package
        self.assertEqual(pkg.install_type, PackageInstallType.HOST)

        pkg = self.LOAD('install-type-valid-images').package
        self.assertEqual(pkg.install_type, PackageInstallType.IMAGES)

        pkg = self.LOAD('install-type-valid-staging').package
        self.assertEqual(pkg.install_type, PackageInstallType.STAGING)

        pkg = self.LOAD('install-type-valid-staging-target').package
        self.assertEqual(pkg.install_type,
            PackageInstallType.STAGING_AND_TARGET)

        pkg = self.LOAD('install-type-valid-target').package
        self.assertEqual(pkg.install_type, PackageInstallType.TARGET)

    def test_pkgconfig_is_internal_disabled(self):
        pkg = self.LOAD('internal-flag-disabled').package
        self.assertFalse(pkg.is_internal)

        pkg = self.LOAD('external-flag-disabled').package
        self.assertTrue(pkg.is_internal)

        pkg = self.LOAD('internal-external-flag-disabled').package
        self.assertFalse(pkg.is_internal)

    def test_pkgconfig_is_internal_enabled(self):
        pkg = self.LOAD('internal-flag-enabled').package
        self.assertTrue(pkg.is_internal)

        pkg = self.LOAD('external-flag-enabled').package
        self.assertFalse(pkg.is_internal)

        pkg = self.LOAD('internal-external-flag-enabled').package
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
        pkg = self.LOAD('missing').package
        self.assertFalse(pkg.is_internal)

    def test_pkgconfig_is_internal_missing_implicit_internal(self):
        # force engine options to default packages to internal
        opts = RelengEngineOptions()
        opts.default_internal_pkgs = True

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg = self.LOAD('missing', manager=manager).package
        self.assertTrue(pkg.is_internal)

    def test_pkgconfig_license_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('license-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('license-invalid-value')

    def test_pkgconfig_license_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.license)

    def test_pkgconfig_license_valid(self):
        pkg = self.LOAD('license-valid-empty').package
        self.assertListEqual(pkg.license, [])

        pkg = self.LOAD('license-valid-multiple-conjunctive').package
        self.assertTupleEqual(pkg.license, (
            'license1',
            'license2',
            'license3',
        ))

        pkg = self.LOAD('license-valid-multiple-disjunctive').package
        self.assertListEqual(pkg.license, [
            'license1',
            'license2',
            'license3',
        ])

        pkg = self.LOAD('license-valid-single').package
        self.assertListEqual(pkg.license, [
            'license',
        ])

        pkg = self.LOAD('license-valid-multiple-mixed1').package
        self.assertListEqual(pkg.license, [
            'A OR B',
            'C AND D',
            'E OR F',
        ])

        pkg = self.LOAD('license-valid-multiple-mixed2').package
        self.assertTupleEqual(pkg.license, (
            'A OR B',
            'C AND D',
            'E OR F',
        ))

    def test_pkgconfig_license_files_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('license-files-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('license-files-invalid-value')

    def test_pkgconfig_license_files_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.license_files)

    def test_pkgconfig_license_files_valid(self):
        pkg = self.LOAD('license-files-valid-empty').package
        self.assertListEqual(pkg.license_files, [])

        pkg = self.LOAD('license-files-valid-multiple').package
        self.assertListEqual(pkg.license_files, [
            'license-file1',
            'license-file2',
            'license-file3',
        ])

        pkg = self.LOAD('license-files-valid-single').package
        self.assertListEqual(pkg.license_files, [
            'license-file',
        ])

    def test_pkgconfig_max_jobs_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('max-jobs-invalid-type')

    def test_pkgconfig_max_jobs_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.max_jobs)

    def test_pkgconfig_max_jobs_valid(self):
        pkg = self.LOAD('max-jobs-valid-positive').package
        self.assertEqual(pkg.max_jobs, 24)

        pkg = self.LOAD('max-jobs-valid-negative').package
        self.assertEqual(pkg.max_jobs, -1)

    def test_pkgconfig_no_extraction_disabled(self):
        pkg = self.LOAD('no-extraction-disabled').package
        self.assertFalse(pkg.no_extraction)

    def test_pkgconfig_no_extraction_enabled(self):
        pkg = self.LOAD('no-extraction-enabled').package
        self.assertTrue(pkg.no_extraction)

    def test_pkgconfig_no_extraction_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('no-extraction-invalid')

    def test_pkgconfig_no_extraction_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.no_extraction)

    def test_pkgconfig_revision_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('revision-invalid-type')

    def test_pkgconfig_revision_valid_explicit(self):
        pkg = self.LOAD('revision-valid-explicit').package
        self.assertEqual(pkg.revision, 'myrevision')

    def test_pkgconfig_revision_valid_implicit(self):
        pkg = self.LOAD('revision-valid-implicit').package
        self.assertEqual(pkg.revision, 'myversion')

    def test_pkgconfig_strip_count_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('strip-count-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('strip-count-invalid-value')

    def test_pkgconfig_strip_count_missing(self):
        pkg = self.LOAD('missing').package
        self.assertEqual(pkg.strip_count, 1)  # default

    def test_pkgconfig_strip_count_valid(self):
        pkg = self.LOAD('strip-count-valid-zero').package
        self.assertEqual(pkg.strip_count, 0)

        pkg = self.LOAD('strip-count-valid-nonzero').package
        self.assertEqual(pkg.strip_count, 2)
