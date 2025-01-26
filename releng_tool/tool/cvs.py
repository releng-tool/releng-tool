# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool

#: executable used to run cvs commands
CVS_COMMAND = 'cvs'

#: list of environment keys to filter from a environment dictionary
CVS_SANITIZE_ENV_KEYS = [
    'CVSIGNORE',
    'CVSREAD',
    'CVSUMASK',
    'CVSWRAPPERS',
    'CVS_SERVER',
]

#: dictionary of environment entries append to the environment dictionary
CVS_EXTEND_ENV = {
    # assume ssh authentication if configured with an :ext: cvsroot
    'CVS_RSH': 'ssh',
}

#: cvs host tool helper
CVS = RelengTool(CVS_COMMAND,
    env_sanitize=CVS_SANITIZE_ENV_KEYS, env_include=CVS_EXTEND_ENV)
