# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

__version__ = '2.5.0'

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

# ruff: noqa: F401
# ruff: noqa: PLC0414

from os.path import join as releng_join
from pathlib import Path as releng_path
from releng_tool.support import releng_include as releng_include
from releng_tool.support import require_version as releng_require_version
from releng_tool.util.env import env_value as releng_env
from releng_tool.util.io import execute as releng_execute
from releng_tool.util.io import execute_rv as releng_execute_rv
from releng_tool.util.io_cat import cat as releng_cat
from releng_tool.util.io_copy import path_copy as releng_copy
from releng_tool.util.io_copy import path_copy_into as releng_copy_into
from releng_tool.util.io_exists import path_exists as releng_exists
from releng_tool.util.io_ls import ls as releng_ls
from releng_tool.util.io_mkdir import mkdir as releng_mkdir
from releng_tool.util.io_move import path_move as releng_move
from releng_tool.util.io_move import path_move_into as releng_move_into
from releng_tool.util.io_remove import path_remove as releng_remove
from releng_tool.util.io_symlink import symlink as releng_symlink
from releng_tool.util.io_temp_dir import temp_dir as releng_tmpdir
from releng_tool.util.io_touch import touch as releng_touch
from releng_tool.util.io_wd import wd as releng_wd
from releng_tool.util.log import debug as debug
from releng_tool.util.log import err as err
from releng_tool.util.log import hint as hint
from releng_tool.util.log import log as log
from releng_tool.util.log import note as note
from releng_tool.util.log import success as success
from releng_tool.util.log import verbose as verbose
from releng_tool.util.log import warn as warn
from releng_tool.util.platform import platform_exit as releng_exit
from releng_tool.util.string import expand as releng_expand
