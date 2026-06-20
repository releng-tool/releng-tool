# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool

#: executable used to run lore commands
LORE_COMMAND = 'lore'

#: lore host tool helper
LORE = RelengTool(LORE_COMMAND)
