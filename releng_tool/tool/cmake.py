# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.tool import RelengTool

#: executable used to run cmake commands
CMAKE_COMMAND = 'cmake'

#: cmake host tool helper
CMAKE = RelengTool(CMAKE_COMMAND)
