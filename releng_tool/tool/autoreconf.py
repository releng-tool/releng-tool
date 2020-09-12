# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from . import RelengTool

#: executable used to run autoreconf commands
AUTORECONF_COMMAND = 'autoreconf'

#: autoreconf host tool helper
AUTORECONF = RelengTool(AUTORECONF_COMMAND) 
