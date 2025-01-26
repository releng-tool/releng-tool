# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool

#: executable used to run rsync commands
RSYNC_COMMAND = 'rsync'

#: list of environment keys to filter from a environment dictionary
RSYNC_SANITIZE_ENV_KEYS = [
    'RSYNC_CHECKSUM_LIST',
    'RSYNC_PARTIAL_DIR',
]

#: rsync host tool helper
RSYNC = RelengTool(RSYNC_COMMAND, env_sanitize=RSYNC_SANITIZE_ENV_KEYS)
