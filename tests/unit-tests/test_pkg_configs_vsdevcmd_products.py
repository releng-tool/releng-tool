# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsVsDevCmdProducts(TestPkgConfigsBase):
    def test_pkgconfig_vsdevcmd_products_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('vsdevcmd-products-invalid-type')

    def test_pkgconfig_vsdevcmd_products_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.vsdevcmd_products)

    def test_pkgconfig_vsdevcmd_products_version(self):
        pkg, _, _ = self.LOAD('vsdevcmd-products-valid')
        self.assertEqual(pkg.vsdevcmd_products,
            'Microsoft.VisualStudio.Product.BuildTools')
