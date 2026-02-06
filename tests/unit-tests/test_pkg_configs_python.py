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
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.python_interpreter)

    def test_pkgconfig_python_interpreter_valid_path(self):
        pkg = self.LOAD('python-interpreter-valid-path').package
        self.assertEqual(pkg.python_interpreter, 'mypython')

    def test_pkgconfig_python_interpreter_valid_str(self):
        pkg = self.LOAD('python-interpreter-valid-str').package
        self.assertEqual(pkg.python_interpreter, 'mypython')

    def test_pkgconfig_python_setup_type_invalid_type(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('python-setup-type-invalid-type')

    def test_pkgconfig_python_setup_type_invalid_value(self):
        with self.assertRaises(RelengToolUnknownPythonSetupType):
            self.LOAD('python-setup-type-invalid-value')

    def test_pkgconfig_python_setup_type_missing(self):
        pkg = self.LOAD('missing').package
        self.assertIsNone(pkg.python_setup_type)

    def test_pkgconfig_python_setup_type_valid_distutils(self):
        pkg = self.LOAD('python-setup-type-valid-distutils').package
        self.assertEqual(pkg.python_setup_type, PythonSetupType.DISTUTILS)

    def test_pkgconfig_python_setup_type_valid_flit(self):
        pkg = self.LOAD('python-setup-type-valid-flit').package
        self.assertEqual(pkg.python_setup_type, PythonSetupType.FLIT)

    def test_pkgconfig_python_setup_type_valid_hatchling(self):
        pkg = self.LOAD('python-setup-type-valid-hatchling').package
        self.assertEqual(pkg.python_setup_type, PythonSetupType.HATCH)

    def test_pkgconfig_python_setup_type_valid_pdm(self):
        pkg = self.LOAD('python-setup-type-valid-pdm').package
        self.assertEqual(pkg.python_setup_type, PythonSetupType.PDM)

    def test_pkgconfig_python_setup_type_valid_pep517(self):
        pkg = self.LOAD('python-setup-type-valid-pep517').package
        self.assertEqual(pkg.python_setup_type, PythonSetupType.PEP517)

    def test_pkgconfig_python_setup_type_valid_poetry(self):
        pkg = self.LOAD('python-setup-type-valid-poetry').package
        self.assertEqual(pkg.python_setup_type, PythonSetupType.POETRY)

    def test_pkgconfig_python_setup_type_valid_setuptools(self):
        pkg = self.LOAD('python-setup-type-valid-setuptools').package
        self.assertEqual(pkg.python_setup_type, PythonSetupType.SETUPTOOLS)
