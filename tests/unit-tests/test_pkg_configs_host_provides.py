# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsHostProvides(TestPkgConfigsBase):
    def test_pkgconfig_host_provides_ignored(self):
        pkg, _, _ = self.LOAD('host-provides-ignored')
        self.assertIsNone(pkg.host_provides)

    def test_pkgconfig_host_provides_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('host-provides-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('host-provides-invalid-value')

    def test_pkgconfig_host_provides_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.host_provides)

    def test_pkgconfig_host_provides_valid(self):
        pkg, _, _ = self.LOAD('host-provides-valid-empty-single')
        self.assertEqual(pkg.host_provides, [''])

        pkg, _, _ = self.LOAD('host-provides-valid-empty-list')
        self.assertEqual(pkg.host_provides, [''])

        pkg, _, _ = self.LOAD('host-provides-valid-single')
        self.assertEqual(pkg.host_provides, ['test-tool'])

        pkg, _, _ = self.LOAD('host-provides-valid-multiple')
        self.assertEqual(pkg.host_provides, ['tool-a', 'tool-b'])
