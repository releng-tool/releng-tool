# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool

#: executable used to run mercurial commands
HG_COMMAND = 'hg'

#: list of environment keys to filter from a environment dictionary
HG_SANITIZE_ENV_KEYS = [
    'HGENCODING',
    'HGENCODINGMODE',
    'HGENCODINGAMBIGUOUS',
    'HGRCPATH',
    'HGPLAIN',
    'HGPLAINEXCEPT',
]

#: dictionary of environment entries append to the environment dictionary
HG_EXTEND_ENV = {
    # hg is most likely a python script; ensure output is unbuffered
    'PYTHONUNBUFFERED': '1',
}

#: mercurial host tool helper
HG = RelengTool(HG_COMMAND,
    env_sanitize=HG_SANITIZE_ENV_KEYS, env_include=HG_EXTEND_ENV)
