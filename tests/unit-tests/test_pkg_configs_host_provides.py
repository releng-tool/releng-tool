# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsHostProvides(TestPkgConfigsBase):
    def test_pkgconfig_host_provides_ignored(self):
        pkg = self.LOAD('host-provides-ignored').package
        self.assertIsNone(pkg.host_provides)

    def test_pkgconfig_host_provides_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('host-provides-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('host-provides-invalid-value')

    def test_pkgconfig_host_provides_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.host_provides)

    def test_pkgconfig_host_provides_valid(self):
        pkg = self.LOAD('host-provides-valid-empty-single').package
        self.assertEqual(pkg.host_provides, [''])

        pkg = self.LOAD('host-provides-valid-empty-list').package
        self.assertEqual(pkg.host_provides, [''])

        pkg = self.LOAD('host-provides-valid-single').package
        self.assertEqual(pkg.host_provides, ['test-tool'])

        pkg = self.LOAD('host-provides-valid-multiple').package
        self.assertEqual(pkg.host_provides, ['tool-a', 'tool-b'])
