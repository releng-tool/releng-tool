# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.tool import RelengTool

#: executable used to run autoreconf commands
AUTORECONF_COMMAND = 'autoreconf'

#: autoreconf host tool helper
AUTORECONF = RelengTool(AUTORECONF_COMMAND)
