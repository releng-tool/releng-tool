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
        deps = self.LOAD('missing').dependencies
        self.assertListEqual(deps, [])

    def test_pkgconfig_deps_valid_deprecated(self):
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

    def test_pkgconfig_needs_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('needs-invalid-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('needs-invalid-value')

    def test_pkgconfig_needs_missing(self):
        needs = self.LOAD('missing').dependencies
        self.assertListEqual(needs, [])

    def test_pkgconfig_needs_valid(self):
        deps = self.LOAD('needs-valid-empty').dependencies
        self.assertListEqual(deps, [])

        deps = self.LOAD('needs-valid-multiple').dependencies
        self.assertListEqual(deps, [
            'dep1',
            'dep2',
            'dep3',
        ])

        deps = self.LOAD('needs-valid-single').dependencies
        self.assertListEqual(deps, [
            'dep',
        ])
