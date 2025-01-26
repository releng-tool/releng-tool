# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool
from releng_tool.util.log import log
from releng_tool.util.log import verbose

#: executable used to run gpg commands
GPG_COMMAND = 'gpg'


class GpgTool(RelengTool):
    """
    gpg host tool

    Provides addition helper methods for gpg-based tool interaction.
    """

    def validate(self, asc, target):
        """
        validate ascii-armored file against a target

        Accepting an ASCII-armored file, use gpg to validate the public key
        against the provided target.

        Args:
            asc: the asc file
            target: the target file

        Returns:
            ``True`` if the target has been validated; ``False`` otherwise
        """

        rv, out = self.execute_rv('--verify', asc, target)
        if rv == 0:
            verbose('validated: {}', asc)
        elif out:
            log(out)

        return rv == 0

#: gpg host tool helper
GPG = GpgTool(GPG_COMMAND)
