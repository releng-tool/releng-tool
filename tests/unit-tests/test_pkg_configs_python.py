# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PythonSetupType
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.exceptions import RelengToolUnknownPythonSetupType
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgPythonConfigs(TestPkgConfigsBase):
    def test_pkgconfig_python_interpreter_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('python-interpreter-invalid-type')

    def test_pkgconfig_python_interpreter_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.python_interpreter)

    def test_pkgconfig_python_interpreter_valid_path(self):
        pkg, _, _ = self.LOAD('python-interpreter-valid-path')
        self.assertEqual(pkg.python_interpreter, 'mypython')

    def test_pkgconfig_python_interpreter_valid_str(self):
        pkg, _, _ = self.LOAD('python-interpreter-valid-str')
        self.assertEqual(pkg.python_interpreter, 'mypython')

    def test_pkgconfig_python_setup_type_invalid_type(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('python-setup-type-invalid-type')

    def test_pkgconfig_python_setup_type_invalid_value(self):
        with self.assertRaises(RelengToolUnknownPythonSetupType):
            self.LOAD('python-setup-type-invalid-value')

    def test_pkgconfig_python_setup_type_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.python_setup_type)

    def test_pkgconfig_python_setup_type_valid_distutils(self):
        pkg, _, _ = self.LOAD('python-setup-type-valid-distutils')
        self.assertEqual(pkg.python_setup_type, PythonSetupType.DISTUTILS)

    def test_pkgconfig_python_setup_type_valid_flit(self):
        pkg, _, _ = self.LOAD('python-setup-type-valid-flit')
        self.assertEqual(pkg.python_setup_type, PythonSetupType.FLIT)

    def test_pkgconfig_python_setup_type_valid_hatchling(self):
        pkg, _, _ = self.LOAD('python-setup-type-valid-hatchling')
        self.assertEqual(pkg.python_setup_type, PythonSetupType.HATCH)

    def test_pkgconfig_python_setup_type_valid_pdm(self):
        pkg, _, _ = self.LOAD('python-setup-type-valid-pdm')
        self.assertEqual(pkg.python_setup_type, PythonSetupType.PDM)

    def test_pkgconfig_python_setup_type_valid_pep517(self):
        pkg, _, _ = self.LOAD('python-setup-type-valid-pep517')
        self.assertEqual(pkg.python_setup_type, PythonSetupType.PEP517)

    def test_pkgconfig_python_setup_type_valid_poetry(self):
        pkg, _, _ = self.LOAD('python-setup-type-valid-poetry')
        self.assertEqual(pkg.python_setup_type, PythonSetupType.POETRY)

    def test_pkgconfig_python_setup_type_valid_setuptools(self):
        pkg, _, _ = self.LOAD('python-setup-type-valid-setuptools')
        self.assertEqual(pkg.python_setup_type, PythonSetupType.SETUPTOOLS)
