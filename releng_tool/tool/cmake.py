# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool

#: executable used to run cmake commands
CMAKE_COMMAND = 'cmake'

#: list of environment keys to filter from a environment dictionary
CMAKE_SANITIZE_ENV_KEYS = [
    # only permit parallel configuration through jobs argument
    'CMAKE_BUILD_PARALLEL_LEVEL',
]

#: cmake host tool helper
CMAKE = RelengTool(CMAKE_COMMAND, env_sanitize=CMAKE_SANITIZE_ENV_KEYS)
