# -*- coding: utf-8 -*-
# Copyright 2018-2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.tool import RelengTool
from releng_tool.util.io import execute
from releng_tool.util.log import debug
from releng_tool.util.win32 import find_win32_python_interpreter
import os
import sys

#: executable used to run python commands
PYTHON_COMMAND = 'python'

#: dictionary of environment entries append to the environment dictionary
PYTHON_EXTEND_ENV = {
    # prevent user site-packages from being included
    'PYTHONNOUSERSITE': '1',
}


class PythonTool(RelengTool):
    """
    python host tool

    Provides addition helper methods for Python-based tool interaction.
    """

    def exists(self):
        """
        return whether or not the host tool exists

        Returns whether or not the tool is available on the host for use.

        Returns:
            ``True``, if the tool exists; ``False`` otherwise
        """
        if self.tool in RelengTool.detected:
            return RelengTool.detected[self.tool]

        found = True
        tool = self.tool

        if execute([tool] + self.exists_args, quiet=True, critical=False):
            found = True
        # if windows and a non-path entry, try to find the interpreter on the
        # local system
        elif sys.platform == 'win32' and os.path.basename(tool) == tool:
            debug('{} tool not available in path; '
                  'attempting to search the system...', tool)
            alt_tool = find_win32_python_interpreter(tool)
            if alt_tool:
                debug('{} tool to be replaced by: {}', tool, alt_tool)

                if execute([alt_tool] + self.exists_args, quiet=True,
                        critical=False):
                    found = True

                    # adjust the tool for this instance to the newly detected
                    # interpreter path
                    tool = alt_tool
                    self.tool = tool

        if found:
            debug('{} tool is detected on this system', tool)
            RelengTool.detected[tool] = True
        else:
            debug('{} tool is not detected on this system', tool)
            RelengTool.detected[tool] = False

        return RelengTool.detected[tool]

    def path(self, sysroot=None, prefix=None):
        """
        return a python path value for the python interpreter

        Returns the expected Python path (``PYTHONPATH``) value for the Python
        interpreter (without a prefix or system root container).

        Args:
            sysroot (optional): system root value to add
            prefix (optional): prefix value to add

        Returns:
            the python path
        """

        if not self.exists():
            return None

        if sysroot is None:
            sysroot = ''

        if prefix is None:
            prefix = ''

        # determine interpreter's major/minor version for determined path
        if not hasattr(self, '_version_cache'):
            output = []
            version = ''
            if self.execute(['-c', "import sys; " +
                    "print('.'.join(map(str, sys.version_info[:2])))"],
                    capture=output, quiet=True):
                version = ''.join(output)
                if sys.platform == 'win32':
                    version = version.replace('.', '')
            self._version_cache = version

        if sys.platform != 'win32':
            base_path = os.path.join(sysroot + prefix,
                'lib', 'python' + self._version_cache)
        else:
            base_path = os.path.join(sysroot + prefix, 'Lib')
        return os.path.join(base_path, 'site-packages')

#: python host tool helper
PYTHON = PythonTool(PYTHON_COMMAND, env_include=PYTHON_EXTEND_ENV)
