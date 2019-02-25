#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

__version__='0.2.0.dev0'

# Below should contain a series of helper implementations to assist releng-tool
# developer's wanting to explicitly import script helpers into scripts not
# directly invoked by releng-tool. When releng-tool invokes a project's script
# (whether it be a configuration script, a package stage-specific script (e.g.
# a package's build script), etc.), a series of utility functions will be made
# available with a pre-populated globals module. If a project defines their own
# Python modules for script support, these modules will not have a graceful way
# to take advantage of these utility methods. To assist developers in this
# situation, utility functions will be included below to expose them into the
# `releng` namespace. A developer with a custom Python script can now import
# specific utility methods using, for example, the following:
#
#     from releng import releng_execute
#
# Note: changes introduced here should be synonymous with engine-shared helpers:
#        RelengEngine._prepareSharedEnvironment

from .util.io import execute as releng_execute
from .util.io import generateTempDir as releng_tmpdir
from .util.io import interimWorkingDirectory as releng_wd
from .util.io import pathCopy as releng_copy
from .util.io import pathExists as releng_exists
from .util.io import pathMove as releng_move
from .util.io import pathRemove as releng_remove
from .util.io import touch as releng_touch
from .util.log import debug as debug
from .util.log import err as err
from .util.log import log as log
from .util.log import note as note
from .util.log import success as success
from .util.log import verbose as verbose
from .util.log import warn as warn
from .util.platform import exit as releng_exit
from .util.string import expand as releng_expand
from os.path import join as releng_join
