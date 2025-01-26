# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool
from releng_tool.util.log import debug
from shutil import which

#: executable used to run scp commands
SCP_COMMAND = 'scp'

#: list of environment keys to filter from a environment dictionary
SCP_SANITIZE_ENV_KEYS = [
    # remove the possibility for authenticated prompts
    'SSH_ASKPASS',
]


class ScpTool(RelengTool):
    """
    scp host tool

    Provides addition helper methods for scp-based tool interaction.
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

        if which(self.tool):
            debug('{} tool is detected on this system', self.tool)
            RelengTool.detected[self.tool] = True
        else:
            debug('{} tool is not detected on this system', self.tool)
            RelengTool.detected[self.tool] = False

        return RelengTool.detected[self.tool]

#: scp host tool helper
SCP = ScpTool(SCP_COMMAND, env_sanitize=SCP_SANITIZE_ENV_KEYS)
