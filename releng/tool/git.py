#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from . import RelengTool

#: executable used to run git commands
GIT_COMMAND = 'git'

#: list of environment keys to filter from a environment dictionary
GIT_SANITIZE_ENV_KEYS = [
    # disable repository location overrides
    'GIT_ALTERNATE_OBJECT_DIRECTORIES',
    'GIT_DIR',
    'GIT_INDEX_FILE',
    'GIT_OBJECT_DIRECTORY',
    'GIT_WORK_TREE',
    # remove the possibility for authenticated prompts
    'GIT_ASKPASS',
    'SSH_ASKPASS',
    # misc
    'GIT_FLUSH',
]

#: git host tool helper
GIT = RelengTool(GIT_COMMAND, env_sanitize=GIT_SANITIZE_ENV_KEYS)
