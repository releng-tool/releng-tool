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
import sysconfig


#: executable used to run python commands
PYTHON_COMMAND = 'python'


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

    def path(self, sysroot, prefix):
        """
        return a site-packages path value for the python interpreter

        Returns the expected site-packages path for the Python interpreter
        as if it was part of a provided system root path. This can be used
        to help register expected paths into `sys.path` or environments based
        on packages that get installed into a host tools sysroot.

        Args:
            sysroot: system root value to add
            prefix: prefix value to add

        Returns:
            the site-packages path
        """

        if not self.exists():
            return None

        syscfg_paths = sysconfig.get_paths()

        try:
            # https://docs.python.org/3/library/sysconfig.html
            # platlib)
            # We use this solely to determine the "site-packages" type;
            # where on Debian, this may vary.
            #  /usr/local/lib/python3.11/dist-packages
            #  C:\Program Files\Python312\Lib\site-packages
            path_platlib = Path(syscfg_paths.get('platlib'))
            # stdlib)
            #  /usr/lib/python3.11
            #  C:\Program Files\Python312\Lib
            path_stdlib = Path(syscfg_paths.get('stdlib'))
        except KeyError:
            return None

        # interpret the current prefix on the stdlib and replace it with the new one
        if sys.platform == 'win32':
            sys_prefix = path_stdlib.parent
        else:
            sys_prefix = path_stdlib.parent.parent

        container = path_stdlib.relative_to(sys_prefix)
        container = Path(prefix or '/') / container

        # remove anchor before we append it ssto the provided sysroot
        container = container.relative_to(container.anchor)

        # build the configured host "site-packages" library path
        return Path(sysroot) / container / path_platlib.name

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
        """

        host_pylib = self.path(sysroot, prefix)

        # include the host environment's site-package folder into the
        # interpreter's system path to allow us to import modules; also
        # register the host path into PYTHONPATH, allowing other packages
        # and scripts to utilize host packages
        self._register_path('PYTHONPATH', str(host_pylib), 'Python-library')

        # if Windows, also register a path to a common scripts folder for
        # Python installation (if host-based Python packages are built)
        if sys.platform == 'win32':
            sdir = str(host_pylib.parent.parent / 'Scripts')
            self._register_path('PATH', sdir, 'Python-Scripts')
        # sanity check that the bin path is already registered; if not, add
        else:
            bdir = str(host_pylib.parent.parent.parent / 'bin')
            self._register_path('PATH', bdir, 'Python-bin')

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
            debug(f'registering {desc} host path: {path}')
            sys.path.insert(0, path)

        insert_env_path(key, path)


#: python host tool helper
PYTHON = PythonTool(PYTHON_COMMAND)
