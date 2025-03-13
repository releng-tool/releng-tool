# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.tool import RelengTool
from releng_tool.util.env import insert_env_path
from releng_tool.util.io import execute
from releng_tool.util.log import debug
from releng_tool.util.win32 import find_win32_python_interpreter
import os
import sys


class PythonTool(RelengTool):
    """
    python host tool

    Provides addition helper methods for Python-based tool interaction.
    """

    def __init__(self, tool=None):
        """
        a python tool

        Provides a series of host tools methods to assist in validating the
        existence of a host tool as well as the execution of a host tool.

        Args:
            tool (optional): the file name of the tool
        """

        if sys.executable:
            default_python_command = sys.executable
        elif sys.platform == 'win32':
            default_python_command = 'python'
        else:
            default_python_command = 'python3'

        super().__init__(tool if tool else default_python_command)

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

        if execute([tool, *self.exists_args], quiet=True, critical=False):
            found = True
        # if windows and a non-path entry, try to find the interpreter on the
        # local system
        elif sys.platform == 'win32' and os.path.basename(tool) == tool:
            debug('{} tool not available in path; '
                  'attempting to search the system...', tool)
            alt_tool = find_win32_python_interpreter(tool)
            if alt_tool:
                debug('{} tool to be replaced by: {}', tool, alt_tool)

                if execute([alt_tool, *self.exists_args], quiet=True,
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

    def scheme(self, prefix):
        """
        return releng-tool's python scheme

        Returns the standard scheme used for all releng-tool processed
        Python packages. Using a fixed scheme ensures consistency across
        various platform when producing a generic sysroot for a project to
        manipulate on.

        Args:
            prefix: prefix for each path

        Returns:
            the scheme dictionary
        """

        final_prefix = prefix.strip('/')

        return {
            'data':        f'{final_prefix}',
            'include':     f'{final_prefix}/include/python',
            'platinclude': f'{final_prefix}/include/python',
            'platlib':     f'{final_prefix}/lib/python',
            'platstdlib':  f'{final_prefix}/lib/python',
            'purelib':     f'{final_prefix}/lib/python',
            'scripts':     f'{final_prefix}/bin',
            'stdlib':      f'{final_prefix}/lib/python',
        }

    def register_host_python(self, sysroot, prefix):
        """
        registers python host library and executable paths into the environment

        With an expected system root path and provided installation prefix,
        register into the global system paths and environment the Python
        library path (site-package) and executable path (bin/Scripts).

        This will extend, if not already registered, the `sys.path`,
        `PYTHONPATH` environment variable and `PATH` environment variable.

        Args:
            sysroot: system root value to add
            prefix: prefix value to add
            scheme: scheme used for the host
        """

        syscfg_paths = self.scheme(prefix)
        sysroot_path = Path(sysroot)

        # include the host environment's site-package folder into the
        # interpreter's system path to allow us to import modules; also
        # register the host path into PYTHONPATH, allowing other packages
        # and scripts to utilize host packages
        libpath = sysroot_path / syscfg_paths['purelib'].removeprefix('/')
        self._register_path('PYTHONPATH', str(libpath), 'library')

        # also register a path to a common scripts folder
        scripts_path = sysroot_path / syscfg_paths['scripts'].removeprefix('/')
        self._register_path('PATH', str(scripts_path), 'scripts')

    def _register_path(self, key: str, path: str, desc: str) -> None:
        """
        registers a path into a provided environment key and `sys.path`

        This call accepts a path to be registered in both `sys.path` and a
        provided environment key. Entries are only updated if the given path
        is not already registered.

        Args:
            key: the environment key to register on
            path: the path to register
            desc: description to include in a debug log indication registration
        """

        if path not in sys.path:
            sys.path.insert(0, str(path))
            debug(f'registered Python-{desc} host path: {path}')

        if insert_env_path(key, path):
            debug(f'registered Python-{desc} in PATH: {path}')


#: python host tool helper
PYTHON = PythonTool()
