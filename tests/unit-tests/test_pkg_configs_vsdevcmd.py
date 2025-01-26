# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsVsDevCmd(TestPkgConfigsBase):
    def test_pkgconfig_vsdevcmd_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('vsdevcmd-invalid-type')

    def test_pkgconfig_vsdevcmd_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.vsdevcmd)

    def test_pkgconfig_vsdevcmd_default(self):
        pkg, _, _ = self.LOAD('vsdevcmd-valid-default')
        self.assertTrue(pkg.vsdevcmd)

    def test_pkgconfig_vsdevcmd_version(self):
        pkg, _, _ = self.LOAD('vsdevcmd-valid-version')
        self.assertEqual(pkg.vsdevcmd, '[16.4,16.5)')
