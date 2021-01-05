# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.tool import RelengTool

#: executable used to run svn commands
SVN_COMMAND = 'svn'

#: list of environment keys to filter from a environment dictionary
SVN_SANITIZE_ENV_KEYS = [
    'SVN_MERGE',
]

#: svn host tool helper
SVN = RelengTool(SVN_COMMAND, env_sanitize=SVN_SANITIZE_ENV_KEYS)
