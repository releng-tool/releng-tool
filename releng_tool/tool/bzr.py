# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool
import sys

#: executable used to run bzr commands
BZR_COMMAND = 'bzr'

#: list of environment keys to filter from a environment dictionary
BZR_SANITIZE_ENV_KEYS = [
    # prevent debugger from loading
    'BZR_PDB',
    # misc
    'BZR_REMOTE_PATH',
    'BZR_TEXTUI_INPUT',
]

#: dictionary of environment entries append to the environment dictionary
BZR_EXTEND_ENV = {
    # always use a progress bar
    'BZR_PROGRESS_BAR': 'text',
}

# always suppress file logging
if sys.platform != 'win32':
    BZR_EXTEND_ENV['BZR_LOG'] = '/dev/null'
else:
    BZR_EXTEND_ENV['BZR_LOG'] = 'NUL'

#: bzr host tool helper
BZR = RelengTool(BZR_COMMAND,
    env_sanitize=BZR_SANITIZE_ENV_KEYS, env_include=BZR_EXTEND_ENV)
