# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolMissingVsDevCmdError
from releng_tool.tool.vswhere import VSWHERE
from releng_tool.util.io import execute_rv
from releng_tool.util.log import debug
from releng_tool.util.log import verbose
import os


def vsdevcmd_initialize(verstr=None, env=None):
    verbose('initializing vsdevcmd...')

    args = ('-property', 'installationPath', '-latest')
    if verstr and not isinstance(verstr, bool):
        args += ('-version', verstr)

    debug('searching for visual studio installation path...')
    rv, output = VSWHERE.execute_rv(*args)
    if rv != 0:
        if output:
            raise RelengToolMissingVsDevCmdError(
                'missing installation', output)

        raise RelengToolMissingVsDevCmdError(
            'non-existent installation path', 'no installations found')

    install_dir = output
    if not os.path.isdir(install_dir):
        raise RelengToolMissingVsDevCmdError(
            'non-existent installation path', install_dir)

    debug('verifying vsdevcmd.bat exists...')
    vsdevcmd = os.path.join(install_dir, 'Common7', 'Tools', 'VsDevCmd.bat')
    if not os.path.isfile(vsdevcmd):
        raise RelengToolMissingVsDevCmdError('missing VsDevCmd.bat', vsdevcmd)

    debug('detecting vsdevcmd variables')
    comspec = os.getenv('COMSPEC', 'cmd.exe')
    invoked_cmd = f'""{vsdevcmd}" && set"'
    rv, output = execute_rv(
        comspec, '/s', '/c', invoked_cmd,
        env_update = {
            # no telemetry
            'VSCMD_SKIP_SENDTELEMETRY': '1',
            # disable startup logo; only looking for installation path
            '__VSCMD_ARG_NO_LOGO': '1',
        },
        args_str=True,
    )
    if rv != 0:
        raise RelengToolMissingVsDevCmdError('VsDevCmd.bat failure', output)

    new_env = {}
    for env_entry in output.splitlines():
        if '=' in env_entry:
            env_key, env_value = env_entry.split('=', 1)
            new_env[env_key] = env_value

    if env:
        env.update(new_env)

    return new_env
