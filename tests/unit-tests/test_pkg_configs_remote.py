# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsRemote(TestPkgConfigsBase):
    def test_pkgconfig_remote_config_disabled(self):
        pkg = self.LOAD('remote-config-disabled').package
        self.assertFalse(pkg.remote_config)

    def test_pkgconfig_remote_config_enabled(self):
        pkg = self.LOAD('remote-config-enabled').package
        self.assertTrue(pkg.remote_config)

    def test_pkgconfig_remote_config_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('remote-config-invalid')

    def test_pkgconfig_remote_config_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.remote_config)

    def test_pkgconfig_remote_scripts_disabled(self):
        pkg = self.LOAD('remote-scripts-disabled').package
        self.assertFalse(pkg.remote_scripts)

    def test_pkgconfig_remote_scripts_enabled(self):
        pkg = self.LOAD('remote-scripts-enabled').package
        self.assertTrue(pkg.remote_scripts)

    def test_pkgconfig_remote_scripts_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('remote-scripts-invalid')

    def test_pkgconfig_remote_scripts_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.remote_scripts)

    def test_pkgconfig_skip_remote_config_disabled_deprecated(self):
        pkg = self.LOAD('skip-remote-config-disabled').package
        self.assertTrue(pkg.remote_config)

    def test_pkgconfig_skip_remote_config_enabled_deprecated(self):
        pkg = self.LOAD('skip-remote-config-enabled').package
        self.assertFalse(pkg.remote_config)

    def test_pkgconfig_skip_remote_config_invalid_deprecated(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('skip-remote-config-invalid')

    def test_pkgconfig_skip_remote_config_missing_deprecated(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.remote_config)

    def test_pkgconfig_skip_remote_scripts_disabled_deprecated(self):
        pkg = self.LOAD('skip-remote-scripts-disabled').package
        self.assertTrue(pkg.remote_scripts)

    def test_pkgconfig_skip_remote_scripts_enabled_deprecated(self):
        pkg = self.LOAD('skip-remote-scripts-enabled').package
        self.assertFalse(pkg.remote_scripts)

    def test_pkgconfig_skip_remote_scripts_invalid_deprecated(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('skip-remote-scripts-invalid')

    def test_pkgconfig_skip_remote_scripts_missing_deprecated(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.remote_scripts)
