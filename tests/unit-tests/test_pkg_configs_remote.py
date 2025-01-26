# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsRemote(TestPkgConfigsBase):
    def test_pkgconfig_remote_config_disabled(self):
        pkg, _, _ = self.LOAD('remote-config-disabled')
        self.assertFalse(pkg.remote_config)

    def test_pkgconfig_remote_config_enabled(self):
        pkg, _, _ = self.LOAD('remote-config-enabled')
        self.assertTrue(pkg.remote_config)

    def test_pkgconfig_remote_config_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('remote-config-invalid')

    def test_pkgconfig_remote_config_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.remote_config)

    def test_pkgconfig_remote_scripts_disabled(self):
        pkg, _, _ = self.LOAD('remote-scripts-disabled')
        self.assertFalse(pkg.remote_scripts)

    def test_pkgconfig_remote_scripts_enabled(self):
        pkg, _, _ = self.LOAD('remote-scripts-enabled')
        self.assertTrue(pkg.remote_scripts)

    def test_pkgconfig_remote_scripts_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('remote-scripts-invalid')

    def test_pkgconfig_remote_scripts_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.remote_scripts)

    def test_pkgconfig_skip_remote_config_disabled_deprecated(self):
        pkg, _, _ = self.LOAD('skip-remote-config-disabled')
        self.assertTrue(pkg.remote_config)

    def test_pkgconfig_skip_remote_config_enabled_deprecated(self):
        pkg, _, _ = self.LOAD('skip-remote-config-enabled')
        self.assertFalse(pkg.remote_config)

    def test_pkgconfig_skip_remote_config_invalid_deprecated(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('skip-remote-config-invalid')

    def test_pkgconfig_skip_remote_config_missing_deprecated(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.remote_config)

    def test_pkgconfig_skip_remote_scripts_disabled_deprecated(self):
        pkg, _, _ = self.LOAD('skip-remote-scripts-disabled')
        self.assertTrue(pkg.remote_scripts)

    def test_pkgconfig_skip_remote_scripts_enabled_deprecated(self):
        pkg, _, _ = self.LOAD('skip-remote-scripts-enabled')
        self.assertFalse(pkg.remote_scripts)

    def test_pkgconfig_skip_remote_scripts_invalid_deprecated(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('skip-remote-scripts-invalid')

    def test_pkgconfig_skip_remote_scripts_missing_deprecated(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.remote_scripts)
