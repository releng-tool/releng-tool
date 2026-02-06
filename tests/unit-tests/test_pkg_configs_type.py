# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PackageType
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.exceptions import RelengToolUnknownPackageType
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsPkgType(TestPkgConfigsBase):
    def test_pkgconfig_type_invalid_type(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('pkg-type-invalid-type')

    def test_pkgconfig_type_invalid_value(self):
        with self.assertRaises(RelengToolUnknownPackageType):
            self.LOAD('pkg-type-invalid-value')

    def test_pkgconfig_type_missing(self):
        pkg = self.LOAD('missing').package
        self.assertEqual(pkg.type, PackageType.SCRIPT)

    def test_pkgconfig_type_valid_autotools(self):
        pkg = self.LOAD('pkg-type-valid-autotools').package
        self.assertEqual(pkg.type, PackageType.AUTOTOOLS)

    def test_pkgconfig_type_valid_cmake(self):
        pkg = self.LOAD('pkg-type-valid-cmake').package
        self.assertEqual(pkg.type, PackageType.CMAKE)

    def test_pkgconfig_type_valid_make(self):
        pkg = self.LOAD('pkg-type-valid-make').package
        self.assertEqual(pkg.type, PackageType.MAKE)

    def test_pkgconfig_type_valid_meson(self):
        pkg = self.LOAD('pkg-type-valid-meson').package
        self.assertEqual(pkg.type, PackageType.MESON)

    def test_pkgconfig_type_valid_python(self):
        pkg = self.LOAD('pkg-type-valid-python').package
        self.assertEqual(pkg.type, PackageType.PYTHON)

    def test_pkgconfig_type_valid_scons(self):
        pkg = self.LOAD('pkg-type-valid-scons').package
        self.assertEqual(pkg.type, PackageType.SCONS)

    def test_pkgconfig_type_valid_script(self):
        pkg = self.LOAD('pkg-type-valid-script').package
        self.assertEqual(pkg.type, PackageType.SCRIPT)
