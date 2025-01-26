# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool
from releng_tool.util.io import execute_rv
from releng_tool.util.log import debug

#: executable used to run tar commands
TAR_COMMAND = 'tar'

#: list of environment keys to filter from a environment dictionary
TAR_SANITIZE_ENV_KEYS = [
    'TAR_OPTIONS',
]


class TarTool(RelengTool):
    """
    tar host tool

    Provides addition helper methods for tar-based tool interaction.

    Attributes:
        force_local: whether or not the `force-local` option is supported
    """

    force_local = False

    def exists(self):
        """
        return whether or not the host tool exists

        Returns whether or not the tool is available on the host for use.

        Returns:
            ``True``, if the tool exists; ``False`` otherwise
        """
        if self.tool in RelengTool.detected:
            return RelengTool.detected[self.tool]

        rv, out = execute_rv(self.tool, '--help')
        if rv == 0:
            debug('{} tool is detected on this system', self.tool)
            if '--force-local' in out:
                debug('{} tool supports force-local', self.tool)
                TarTool.force_local = True
            else:
                debug('{} tool does not support force-local', self.tool)
            RelengTool.detected[self.tool] = True
        else:
            debug('{} tool is not detected on this system', self.tool)
            RelengTool.detected[self.tool] = False

        return RelengTool.detected[self.tool]

#: tar host tool helper
TAR = TarTool(TAR_COMMAND, env_sanitize=TAR_SANITIZE_ENV_KEYS)
