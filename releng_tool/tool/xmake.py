# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool

#: executable used to run xmake commands
XMAKE_COMMAND = 'xmake'

#: list of environment keys to filter from a environment dictionary
XMAKE_SANITIZE_ENV_KEYS = [
    'XMAKE_CONFIGDIR',
    'XMAKE_GLOBALDIR',
    'XMAKE_RCFILES',
]

#: xmake host tool helper
XMAKE = RelengTool(XMAKE_COMMAND, env_sanitize=XMAKE_SANITIZE_ENV_KEYS)
