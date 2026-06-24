# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool

#: executable used to run xmake commands
XMAKE_COMMAND = 'xmake'

#: dictionary of environment entries append to the environment dictionary
MESON_EXTEND_ENV = {
    # xmake should not be run as root, but the same applies for using
    # releng-tool in general for other package types; releng-tool comes with
    # an elevated user check to stop or warn users already, and we do not want
    # only the xmake utility stacking this enforcement; leave the check off
    # to be flexible for single user container builds
    'XMAKE_ROOT': 'y',
}

#: list of environment keys to filter from a environment dictionary
XMAKE_SANITIZE_ENV_KEYS = [
    'XMAKE_CONFIGDIR',
    'XMAKE_GLOBALDIR',
    'XMAKE_RCFILES',
]

#: xmake host tool helper
XMAKE = RelengTool(
    XMAKE_COMMAND,
    env_include=MESON_EXTEND_ENV,
    env_sanitize=XMAKE_SANITIZE_ENV_KEYS,
)
