# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsNeeds(TestPkgConfigsBase):
    def test_pkgconfig_deps_invalid_deprecated(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('deps-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('deps-invalid-value')

    def test_pkgconfig_deps_missing_deprecated(self):
        _, _, deps = self.LOAD('missing')
        self.assertListEqual(deps, [])

    def test_pkgconfig_deps_valid_deprecated(self):
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

    def test_pkgconfig_needs_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('needs-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('needs-invalid-value')

    def test_pkgconfig_needs_missing(self):
        _, _, needs = self.LOAD('missing')
        self.assertListEqual(needs, [])

    def test_pkgconfig_needs_valid(self):
        _, _, deps = self.LOAD('needs-valid-empty')
        self.assertListEqual(deps, [])

        _, _, deps = self.LOAD('needs-valid-multiple')
        self.assertListEqual(deps, [
            'dep1',
            'dep2',
            'dep3',
        ])

        _, _, deps = self.LOAD('needs-valid-single')
        self.assertListEqual(deps, [
            'dep',
        ])
