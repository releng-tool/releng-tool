# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests.support.python_tool_test import PythonSiteToolBase


class TestToolPythonPdmLegacy(PythonSiteToolBase):
    def tool_template(self):
        return 'python-pdm-legacy'

    def test_tool_python_pdm_legacy_default_scheme_default(self):
        rv = self.engine.run()
        self.assertTrue(rv)

        lib_python = self.python_lib(self.engine.opts.host_dir)
        self.assertFalse(lib_python.is_dir())

        lib_python = self.python_lib(self.engine.opts.staging_dir)
        self.assertFalse(lib_python.is_dir())

        lib_python = self.python_lib(self.engine.opts.target_dir)
        self.assertTrue(lib_python.is_dir())
        self.assertPythonModuleExists(lib_python, 'hello_module')

    def test_tool_python_pdm_legacy_default_scheme_native(self):
        self.defconfig_add('PYTHON_INSTALLER_SCHEME', 'native')

        rv = self.engine.run()
        self.assertTrue(rv)

        site_packages = self.find_site_packages(self.engine.opts.host_dir)
        self.assertIsNone(site_packages)

        site_packages = self.find_site_packages(self.engine.opts.staging_dir)
        self.assertIsNone(site_packages)

        site_packages = self.find_site_packages(self.engine.opts.target_dir)
        self.assertIsNotNone(site_packages)
        self.assertPythonModuleExists(site_packages, 'hello_module')

    def test_tool_python_pdm_legacy_host_scheme_default(self):
        self.defconfig_add('INSTALL_TYPE', 'host')

        rv = self.engine.run()
        self.assertTrue(rv)

        lib_python = self.python_lib(self.engine.opts.host_dir)
        self.assertTrue(lib_python.is_dir())
        self.assertPythonModuleExists(lib_python, 'hello_module')

        lib_python = self.python_lib(self.engine.opts.staging_dir)
        self.assertFalse(lib_python.is_dir())

        lib_python = self.python_lib(self.engine.opts.target_dir)
        self.assertFalse(lib_python.is_dir())

    def test_tool_python_pdm_legacy_host_scheme_native(self):
        self.defconfig_add('INSTALL_TYPE', 'host')
        self.defconfig_add('PYTHON_INSTALLER_SCHEME', 'native')

        rv = self.engine.run()
        self.assertTrue(rv)

        site_packages = self.find_site_packages(self.engine.opts.host_dir)
        self.assertIsNotNone(site_packages)
        self.assertPythonModuleExists(site_packages, 'hello_module')

        site_packages = self.find_site_packages(self.engine.opts.staging_dir)
        self.assertIsNone(site_packages)

        site_packages = self.find_site_packages(self.engine.opts.target_dir)
        self.assertIsNone(site_packages)

    def test_tool_python_pdm_legacy_staging_scheme_default(self):
        self.defconfig_add('INSTALL_TYPE', 'staging')

        rv = self.engine.run()
        self.assertTrue(rv)

        lib_python = self.python_lib(self.engine.opts.host_dir)
        self.assertFalse(lib_python.is_dir())

        lib_python = self.python_lib(self.engine.opts.staging_dir)
        self.assertTrue(lib_python.is_dir())
        self.assertPythonModuleExists(lib_python, 'hello_module')

        lib_python = self.python_lib(self.engine.opts.target_dir)
        self.assertFalse(lib_python.is_dir())

    def test_tool_python_pdm_legacy_staging_scheme_native(self):
        self.defconfig_add('INSTALL_TYPE', 'staging')
        self.defconfig_add('PYTHON_INSTALLER_SCHEME', 'native')

        rv = self.engine.run()
        self.assertTrue(rv)

        site_packages = self.find_site_packages(self.engine.opts.host_dir)
        self.assertIsNone(site_packages)

        site_packages = self.find_site_packages(self.engine.opts.staging_dir)
        self.assertIsNotNone(site_packages)
        self.assertPythonModuleExists(site_packages, 'hello_module')

        site_packages = self.find_site_packages(self.engine.opts.target_dir)
        self.assertIsNone(site_packages)

    def test_tool_python_pdm_legacy_staging_and_target_scheme_default(self):
        self.defconfig_add('INSTALL_TYPE', 'staging_and_target')

        rv = self.engine.run()
        self.assertTrue(rv)

        lib_python = self.python_lib(self.engine.opts.host_dir)
        self.assertFalse(lib_python.is_dir())

        lib_python = self.python_lib(self.engine.opts.staging_dir)
        self.assertTrue(lib_python.is_dir())
        self.assertPythonModuleExists(lib_python, 'hello_module')

        lib_python = self.python_lib(self.engine.opts.target_dir)
        self.assertTrue(lib_python.is_dir())
        self.assertPythonModuleExists(lib_python, 'hello_module')

    def test_tool_python_pdm_legacy_staging_and_target_scheme_native(self):
        self.defconfig_add('INSTALL_TYPE', 'staging_and_target')
        self.defconfig_add('PYTHON_INSTALLER_SCHEME', 'native')

        rv = self.engine.run()
        self.assertTrue(rv)

        site_packages = self.find_site_packages(self.engine.opts.host_dir)
        self.assertIsNone(site_packages)

        site_packages = self.find_site_packages(self.engine.opts.staging_dir)
        self.assertIsNotNone(site_packages)
        self.assertPythonModuleExists(site_packages, 'hello_module')

        site_packages = self.find_site_packages(self.engine.opts.target_dir)
        self.assertIsNotNone(site_packages)
        self.assertPythonModuleExists(site_packages, 'hello_module')
