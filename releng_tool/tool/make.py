# -*- coding: utf-8 -*-
# Copyright 2018-2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.tool import RelengTool

#: executable used to run make commands
MAKE_COMMAND = 'make'

#: make host tool helper
MAKE = RelengTool(MAKE_COMMAND)
