# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgPythonConfigsInstallerLauncherKind(TestPkgConfigsBase):
    def test_pkgconfig_python_installer_launcher_kind_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('python-installer-launcher-kind-invalid-type')

    def test_pkgconfig_python_installer_launcher_kind_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.python_installer_launcher_kind)

    def test_pkgconfig_python_installer_launcher_kind_valid_posix(self):
        pkg, _, _ = self.LOAD('python-installer-launcher-kind-valid-posix')
        self.assertEqual(pkg.python_installer_launcher_kind, 'posix')

    def test_pkgconfig_python_installer_launcher_kind_valid_win_amd64(self):
        pkg, _, _ = self.LOAD('python-installer-launcher-kind-valid-win-amd64')
        self.assertEqual(pkg.python_installer_launcher_kind, 'win-amd64')

    def test_pkgconfig_python_installer_launcher_kind_valid_win_arm64(self):
        pkg, _, _ = self.LOAD('python-installer-launcher-kind-valid-win-arm64')
        self.assertEqual(pkg.python_installer_launcher_kind, 'win-arm64')

    def test_pkgconfig_python_installer_launcher_kind_valid_win_arm(self):
        pkg, _, _ = self.LOAD('python-installer-launcher-kind-valid-win-arm')
        self.assertEqual(pkg.python_installer_launcher_kind, 'win-arm')

    def test_pkgconfig_python_installer_launcher_kind_valid_win_ia32(self):
        pkg, _, _ = self.LOAD('python-installer-launcher-kind-valid-win-ia32')
        self.assertEqual(pkg.python_installer_launcher_kind, 'win-ia32')
