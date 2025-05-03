# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgPythonConfigsInstallerInterpreter(TestPkgConfigsBase):
    def test_pkgconfig_python_installer_interpreter_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('python-installer-interpreter-invalid-type')

    def test_pkgconfig_python_installer_interpreter_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.python_installer_interpreter)

    def test_pkgconfig_python_installer_interpreter_valid(self):
        pkg, _, _ = self.LOAD('python-installer-interpreter-valid')
        self.assertEqual(pkg.python_installer_interpreter, 'custom/path')
