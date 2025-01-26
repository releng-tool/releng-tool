# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool
import sys

#: executable used to run brz commands
BRZ_COMMAND = 'brz'

#: list of environment keys to filter from a environment dictionary
BRZ_SANITIZE_ENV_KEYS = [
    # prevent debugger from loading
    'BRZ_PDB',
    # misc
    'BRZ_REMOTE_PATH',  # does not appear to exist, but be ready
    'BRZ_TEXTUI_INPUT',
    'BZR_REMOTE_PATH',  # still looks to be bzr-prefixed
]

#: dictionary of environment entries append to the environment dictionary
BRZ_EXTEND_ENV = {
    # always use a progress bar
    'BRZ_PROGRESS_BAR': 'text',
}

# always suppress file logging
if sys.platform != 'win32':
    BRZ_EXTEND_ENV['BRZ_LOG'] = '/dev/null'
else:
    BRZ_EXTEND_ENV['BRZ_LOG'] = 'NUL'

#: brz host tool helper
BRZ = RelengTool(BRZ_COMMAND,
    env_sanitize=BRZ_SANITIZE_ENV_KEYS, env_include=BRZ_EXTEND_ENV)
