# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests.support.python_tool_test import PythonSiteToolBase
import sys


class TestToolPythonNative(PythonSiteToolBase):
    def tool_template(self):
        return 'python-native'

    def test_tool_python_native_interpreter(self):
        self.defconfig_add('PYTHON_INTERPRETER', sys.executable)

        rv = self.engine.run()
        self.assertTrue(rv)

        lib_python = self.python_lib(self.engine.opts.target_dir)
        self.assertTrue(lib_python.is_dir())
        self.assertPythonModuleExists(lib_python, 'hello_module')
