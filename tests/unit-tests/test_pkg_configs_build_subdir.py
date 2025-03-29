# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.exceptions import RelengToolPathPackageTraversal
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsBuildSubdir(TestPkgConfigsBase):
    def test_pkgconfig_build_subdir_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('build-subdir-invalid-type')

    def test_pkgconfig_build_subdir_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.build_subdir)

    def test_pkgconfig_build_subdir_traversal(self):
        with self.assertRaises(RelengToolPathPackageTraversal):
            self.LOAD('build-subdir-traversal')

    def test_pkgconfig_build_subdir_valid_path(self):
        pkg, _, _ = self.LOAD('build-subdir-valid-path')
        self.assertTrue(pkg.build_subdir.endswith('subdir'))

    def test_pkgconfig_build_subdir_valid_str(self):
        pkg, _, _ = self.LOAD('build-subdir-valid-str')
        self.assertTrue(pkg.build_subdir.endswith('subdir'))
