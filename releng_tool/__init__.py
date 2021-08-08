# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

__version__ = '0.8.0.dev0'

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

# flake8: noqa
from os.path import join as releng_join
from releng_tool.util.env import set_env_value as releng_env
from releng_tool.util.io import ensure_dir_exists as releng_mkdir
from releng_tool.util.io import execute as releng_execute
from releng_tool.util.io import generate_temp_dir as releng_tmpdir
from releng_tool.util.io import interim_working_dir as releng_wd
from releng_tool.util.io import path_copy as releng_copy
from releng_tool.util.io import path_exists as releng_exists
from releng_tool.util.io import path_move as releng_move
from releng_tool.util.io import path_remove as releng_remove
from releng_tool.util.io import touch as releng_touch
from releng_tool.util.log import debug as debug
from releng_tool.util.log import err as err
from releng_tool.util.log import log as log
from releng_tool.util.log import note as note
from releng_tool.util.log import success as success
from releng_tool.util.log import verbose as verbose
from releng_tool.util.log import warn as warn
from releng_tool.util.platform import platform_exit as releng_exit
from releng_tool.util.string import expand as releng_expand
