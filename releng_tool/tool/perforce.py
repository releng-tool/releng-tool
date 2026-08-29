# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool

#: executable used to run perforce commands
PERFORCE_COMMAND = 'p4'

#: perforce host tool helper
PERFORCE = RelengTool(PERFORCE_COMMAND, exists_args=['-V'])
