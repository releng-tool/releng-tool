# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from releng_tool.tool import RelengTool
from releng_tool.util.log import debug
import distutils.spawn

#: executable used to run rsync commands
RSYNC_COMMAND = 'rsync'

#: list of environment keys to filter from a environment dictionary
RSYNC_SANITIZE_ENV_KEYS = [
    'RSYNC_CHECKSUM_LIST',
    'RSYNC_PARTIAL_DIR',
]

class RsyncTool(RelengTool):
    """
    rsync host tool

    Provides addition helper methods for rsync-based tool interaction.
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

        if distutils.spawn.find_executable(self.tool):
            debug('{} tool is detected on this system', self.tool)
            RelengTool.detected[self.tool] = True
        else:
            debug('{} tool is not detected on this system', self.tool)
            RelengTool.detected[self.tool] = False

        return RelengTool.detected[self.tool]

#: rsync host tool helper
RSYNC = RsyncTool(RSYNC_COMMAND, env_sanitize=RSYNC_SANITIZE_ENV_KEYS)
