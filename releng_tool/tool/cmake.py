# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.tool import RelengTool

#: executable used to run cmake commands
CMAKE_COMMAND = 'cmake'

#: cmake host tool helper
CMAKE = RelengTool(CMAKE_COMMAND)
