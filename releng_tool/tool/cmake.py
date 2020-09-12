# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from . import RelengTool

#: executable used to run cmake commands
CMAKE_COMMAND = 'cmake'

#: cmake host tool helper
CMAKE = RelengTool(CMAKE_COMMAND) 
