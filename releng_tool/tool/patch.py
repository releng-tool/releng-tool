# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool

#: executable used to run patch commands
PATCH_COMMAND = 'patch'

#: list of environment keys to filter from a environment dictionary
PATCH_SANITIZE_ENV_KEYS = [
    'PATCH_GET',
    'PATCH_VERSION_CONTROL',
    'POSIXLY_CORRECT',
    'QUOTING_STYLE',
    'SIMPLE_BACKUP_SUFFIX',
    'VERSION_CONTROL',
]

#: patch host tool helper
PATCH = RelengTool(PATCH_COMMAND, env_sanitize=PATCH_SANITIZE_ENV_KEYS)
