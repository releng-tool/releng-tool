# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.exceptions import RelengToolPathPackageTraversal
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsPrefix(TestPkgConfigsBase):
    def test_pkgconfig_prefix_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('prefix-invalid-type')

    def test_pkgconfig_prefix_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.prefix)

    def test_pkgconfig_prefix_traversal(self):
        with self.assertRaises(RelengToolPathPackageTraversal):
            self.LOAD('prefix-traversal')

    def test_pkgconfig_prefix_valid_path(self):
        pkg, _, _ = self.LOAD('prefix-valid-path')
        self.assertEqual(pkg.prefix, 'myprefix')

    def test_pkgconfig_prefix_valid_str(self):
        pkg, _, _ = self.LOAD('prefix-valid-str')
        self.assertEqual(pkg.prefix, 'myprefix')
