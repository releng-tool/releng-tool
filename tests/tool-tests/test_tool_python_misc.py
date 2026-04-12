# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.engine.python.install import RelengToolPythonSchemeInstallTraversal
from tests import setpkgcfg
from tests.support.python_tool_test import PythonSiteToolBase


class TestToolPythonMisc(PythonSiteToolBase):
    def tool_template(self):
        return 'python-native'

    def test_tool_python_misc_scheme_traversal(self):
        setpkgcfg(self.engine, 'test', Rpk.PYTHON_INSTALLER_SCHEME, {
            'data':        '',
            'include':     'include/python',
            'platinclude': 'include/python',
            'platlib':     'lib/python',
            'platstdlib':  'lib/python',
            'purelib':     '..',  # try to use a path outside
            'scripts':     'bin',
            'stdlib':      'lib/python',
        })

        with self.assertRaises(RelengToolPythonSchemeInstallTraversal):
            self.engine.run()
