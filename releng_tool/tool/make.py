# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from . import RelengTool

#: executable used to run make commands
MAKE_COMMAND = 'make'

#: make host tool helper
MAKE = RelengTool(MAKE_COMMAND)
