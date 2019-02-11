#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from . import RelengTool

#: executable used to run cvs commands
CVS_COMMAND = 'cvs'

#: list of environment keys to filter from a environment dictionary
CVS_SANITIZE_ENV_KEYS = [
    'CVSIGNORE',
    'CVSREAD',
    'CVSUMASK',
    'CVSWRAPPERS',
    'CVS_RSH',
    'CVS_SERVER',
]

#: cvs host tool helper
CVS = RelengTool(CVS_COMMAND, env_sanitize=CVS_SANITIZE_ENV_KEYS) 
