# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.exceptions import RelengToolPathPackageTraversal
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsPatchSubdir(TestPkgConfigsBase):
    def test_pkgconfig_patch_subdir_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('patch-subdir-invalid-type')

    def test_pkgconfig_patch_subdir_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.patch_subdir)

    def test_pkgconfig_patch_subdir_traversal(self):
        with self.assertRaises(RelengToolPathPackageTraversal):
            self.LOAD('patch-subdir-traversal')

    def test_pkgconfig_patch_subdir_valid_path(self):
        pkg, _, _ = self.LOAD('patch-subdir-valid-path')
        self.assertTrue(pkg.patch_subdir.endswith('patch-subdir'))

    def test_pkgconfig_patch_subdir_valid_str(self):
        pkg, _, _ = self.LOAD('patch-subdir-valid-str')
        self.assertTrue(pkg.patch_subdir.endswith('patch-subdir'))
