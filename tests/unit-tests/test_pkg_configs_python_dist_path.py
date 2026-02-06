# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgPythonConfigsDistPath(TestPkgConfigsBase):
    def test_pkgconfig_python_dist_path_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('python-dist-path-invalid-type')

    def test_pkgconfig_python_dist_path_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.python_dist_path)

    def test_pkgconfig_python_dist_path_valid_path(self):
        pkg = self.LOAD('python-dist-path-valid-path').package
        self.assertEqual(pkg.python_dist_path, 'dist2')

    def test_pkgconfig_python_dist_path_valid_str(self):
        pkg = self.LOAD('python-dist-path-valid-str').package
        self.assertEqual(pkg.python_dist_path, 'dist2')
