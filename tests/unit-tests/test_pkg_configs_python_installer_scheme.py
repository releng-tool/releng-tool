# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgPythonConfigsInstallerScheme(TestPkgConfigsBase):
    def test_pkgconfig_python_installer_scheme_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('python-installer-scheme-invalid-type')

    def test_pkgconfig_python_installer_scheme_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.python_installer_scheme)

    def test_pkgconfig_python_installer_scheme_valid_custom(self):
        pkg, _, _ = self.LOAD('python-installer-scheme-valid-custom')
        self.assertDictEqual(pkg.python_installer_scheme, {
            'data':        '',
            'include':     'myinclude/python',
            'platinclude': 'myinclude/python',
            'platlib':     'mylib/python',
            'platstdlib':  'mylib/python',
            'purelib':     'mylib/python',
            'scripts':     'mybin',
            'stdlib':      'mylib/python',
        })

    def test_pkgconfig_python_installer_scheme_valid_native(self):
        pkg, _, _ = self.LOAD('python-installer-scheme-valid-native')
        self.assertEqual(pkg.python_installer_scheme, 'native')

    def test_pkgconfig_python_installer_scheme_valid_stock(self):
        pkg, _, _ = self.LOAD('python-installer-scheme-valid-stock')
        self.assertEqual(pkg.python_installer_scheme, 'posix_prefix')
