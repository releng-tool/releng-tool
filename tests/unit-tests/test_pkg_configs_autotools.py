# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsAutotools(TestPkgConfigsBase):
    def test_pkgconfig_autotools_autoreconf_disabled(self):
        pkg, _, _ = self.LOAD('autotools-autoreconf-disabled')
        self.assertFalse(pkg.autotools_autoreconf)

    def test_pkgconfig_autotools_autoreconf_enabled(self):
        pkg, _, _ = self.LOAD('autotools-autoreconf-enabled')
        self.assertTrue(pkg.autotools_autoreconf)

    def test_pkgconfig_autotools_autoreconf_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('autotools-autoreconf-invalid')

    def test_pkgconfig_autotools_autoreconf_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.autotools_autoreconf)
