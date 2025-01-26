# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool

#: executable used to run make commands
MAKE_COMMAND = 'make'

#: make host tool helper
MAKE = RelengTool(MAKE_COMMAND)
