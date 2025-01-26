# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsGit(TestPkgConfigsBase):
    def test_pkgconfig_git_config_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('git-config-invalid-base-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('git-config-invalid-key-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('git-config-invalid-strs')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('git-config-invalid-value-type')

    def test_pkgconfig_git_config_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.git_config)

        pkg, _, _ = self.LOAD('conf-defs-valid')
        self.assertIsNone(pkg.git_config)

        pkg, _, _ = self.LOAD('install-defs-valid')
        self.assertIsNone(pkg.git_config)

    def test_pkgconfig_git_config_valid(self):
        pkg, _, _ = self.LOAD('git-config-valid')
        self.assertDictEqual(pkg.git_config, {
            'key1': 'val1',
            'key2': None,
            'key3': 'val3',
        })

    def test_pkgconfig_git_depth_invalid_type(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('git-depth-invalid-type')

    def test_pkgconfig_git_depth_invalid_value(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('git-depth-invalid-value')

    def test_pkgconfig_git_depth_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.git_depth)

    def test_pkgconfig_git_depth_valid_nonzero(self):
        pkg, _, _ = self.LOAD('git-depth-valid-nonzero')
        self.assertEqual(pkg.git_depth, 50)

    def test_pkgconfig_git_depth_valid_zero(self):
        pkg, _, _ = self.LOAD('git-depth-valid-zero')
        self.assertEqual(pkg.git_depth, 0)

    def test_pkgconfig_git_refspecs_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('git-refspecs-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('git-refspecs-invalid-value')

    def test_pkgconfig_git_refspecs_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.git_refspecs)

    def test_pkgconfig_git_refspecs_valid(self):
        pkg, _, _ = self.LOAD('git-refspecs-valid-empty')
        self.assertListEqual(pkg.git_refspecs, [])

        pkg, _, _ = self.LOAD('git-refspecs-valid-multiple')
        self.assertListEqual(pkg.git_refspecs, [
            'refspec1',
            'refspec2',
            'refspec3',
        ])

        pkg, _, _ = self.LOAD('git-refspecs-valid-single')
        self.assertListEqual(pkg.git_refspecs, [
            'refspec',
        ])

    def test_pkgconfig_git_submodules_disabled(self):
        pkg, _, _ = self.LOAD('git-submodules-disabled')
        self.assertFalse(pkg.git_submodules)

    def test_pkgconfig_git_submodules_enabled(self):
        pkg, _, _ = self.LOAD('git-submodules-enabled')
        self.assertTrue(pkg.git_submodules)

    def test_pkgconfig_git_submodules_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('git-submodules-invalid')

    def test_pkgconfig_git_submodules_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.git_submodules)

    def test_pkgconfig_git_verify_disabled(self):
        pkg, _, _ = self.LOAD('git-verify-disabled')
        self.assertFalse(pkg.git_verify_revision)

    def test_pkgconfig_git_verify_enabled(self):
        pkg, _, _ = self.LOAD('git-verify-enabled')
        self.assertTrue(pkg.git_verify_revision)

    def test_pkgconfig_git_verify_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('git-verify-invalid')

    def test_pkgconfig_git_verify_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.git_verify_revision)
