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
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.prefix)

    def test_pkgconfig_prefix_traversal(self):
        with self.assertRaises(RelengToolPathPackageTraversal):
            self.LOAD('prefix-traversal')

    def test_pkgconfig_prefix_valid_path(self):
        pkg = self.LOAD('prefix-valid-path').package
        self.assertEqual(pkg.prefix, 'myprefix')

    def test_pkgconfig_prefix_valid_str(self):
        pkg = self.LOAD('prefix-valid-str').package
        self.assertEqual(pkg.prefix, 'myprefix')
