#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from . import RelengTool
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

        if not sysroot:
            sysroot = ''

        if not prefix:
            prefix = ''

        # determine interpreter's major/minor version for determined path
        if not hasattr(self, '_version_cache'):
            output = []
            version = ''
            if self.execute(['-c', "import sys; " +
                    "print('.').join(map(str, sys.version_info[:2]))"],
                    capture=output):
                version = ''.join(output)
                if sys.platform == 'win32':
                    version = version.replace('.', '')
            self._version_cache = version

        if sys.platform != 'win32':
            base_path = os.path.join(sysroot + prefix,
                'lib', 'python' + self._version_cache)
        else:
            base_path = os.path.join(sysroot,
                'Python' + self._version_cache, 'Lib')
        return os.path.join(base_path, 'site-packages')

#: python host tool helper
PYTHON = PythonTool(PYTHON_COMMAND, env_include=PYTHON_EXTEND_ENV)
