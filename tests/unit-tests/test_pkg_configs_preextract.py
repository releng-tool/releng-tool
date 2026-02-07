# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsPreextract(TestPkgConfigsBase):
    def test_pkgconfig_preextract_disabled(self):
        pkg = self.LOAD('preextract-disabled').package
        self.assertFalse(pkg.preextract)

    def test_pkgconfig_preextract_enabled(self):
        pkg = self.LOAD('preextract-enabled').package
        self.assertTrue(pkg.preextract)

    def test_pkgconfig_preextract_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('preextract-invalid')

    def test_pkgconfig_preextract_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.preextract)
