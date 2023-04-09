# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.tool import RelengTool

#: executable used to run autoreconf commands
AUTORECONF_COMMAND = 'autoreconf'

#: autoreconf host tool helper
AUTORECONF = RelengTool(AUTORECONF_COMMAND)
