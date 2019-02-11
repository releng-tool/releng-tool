#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from . import RelengTool

#: executable used to run tar commands
TAR_COMMAND = 'tar'

#: list of environment keys to filter from a environment dictionary
TAR_SANITIZE_ENV_KEYS = [
    'TAR_OPTIONS',
]

#: tar host tool helper
TAR = RelengTool(TAR_COMMAND, env_sanitize=TAR_SANITIZE_ENV_KEYS)
