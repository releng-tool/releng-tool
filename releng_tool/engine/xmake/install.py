# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.xmake import XMAKE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def install(opts):
    """
    support installation xmake projects

    With provided installation options (``RelengInstallOptions``), the
    installation stage will be processed.

    Args:
        opts: installation options

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    if not XMAKE.exists():
        err('unable to install package; xmake is not installed')
        return False

    # default definitions
    xmake_defs = {
    }
    if opts.install_defs:
        xmake_defs.update(expand(opts.install_defs))

    # default options
    xmake_opts = {
    }
    if opts.install_opts:
        xmake_opts.update(expand(opts.install_opts))

    # argument building
    xmake_args = [
        'install',
    ]

    xmake_args.extend(prepare_definitions(xmake_defs))
    xmake_args.extend(prepare_arguments(xmake_opts))

    # default environment
    xmake_env = {
        'XMAKE_CONFIGDIR': opts.build_output_dir,
    }
    if opts.install_env:
        xmake_env.update(expand(opts.install_env))

    # install to each destination
    for dest_dir in opts.dest_dirs:
        prefixed_dest_dir = dest_dir + opts.prefix
        xmake_args_tmp = list(xmake_args)
        xmake_args_tmp.append(f'--installdir={prefixed_dest_dir}')
        if not XMAKE.execute(xmake_args_tmp, env=xmake_env):
            err('failed to install xmake project: {}', opts.name)
            return False

    return True
