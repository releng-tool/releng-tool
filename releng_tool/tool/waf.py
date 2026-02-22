# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool

#: executable used to run waf commands
WAF_COMMAND = 'waf'

#: list of environment keys to filter from a environment dictionary
WAF_SANITIZE_ENV_KEYS = [
    'JOBS',
    'NOCLIMB',
    'NUMBER_OF_PROCESSORS',
    'WAFDIR',
    'WAFLOCK',
]

#: waf host tool helper
WAF = RelengTool(WAF_COMMAND, env_sanitize=WAF_SANITIZE_ENV_KEYS)
