# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.tool import RelengTool
from releng_tool.util.io import execute_rv
from releng_tool.util.log import debug
import os

#: executable used to run vswhere commands
VSWHERE_COMMAND = 'vswhere'


class VsWhereTool(RelengTool):
    """
    vswhere host tool

    Provides addition helper methods for vswhere-based tool interaction.
    """

    def exists(self):
        """
        return whether the host tool exists

        Returns whether the tool is available on the host for use.

        Returns:
            ``True``, if the tool exists; ``False`` otherwise
        """
        if self.tool in RelengTool.detected:
            return RelengTool.detected[self.tool]

        rv, _ = execute_rv(self.tool, '/?')
        if rv == 0:
            debug(f'tool is detected on this system: {self.tool}')
            RelengTool.detected[self.tool] = True
        else:
            pfx86 = Path(os.getenv(
                'PROGRAMFILES(X86)',
                'C:\\Program Files (x86)'))
            standard_vswhere_path = pfx86 / 'Microsoft Visual Studio' \
                / 'Installer' / 'vswhere.exe'

            if standard_vswhere_path.exists():
                self.tool = standard_vswhere_path
                debug(f'tool is detected on this system: {self.tool}')
                RelengTool.detected[self.tool] = True
            else:
                debug(f'tool is not detected on this system: {self.tool}')
                RelengTool.detected[self.tool] = False

        return RelengTool.detected[self.tool]


#: vswhere host tool helper
VSWHERE = VsWhereTool(VSWHERE_COMMAND)
