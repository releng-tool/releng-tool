# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.waf import WAF
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def install(opts):
    """
    support installation waf projects

    With provided installation options (``RelengInstallOptions``), the
    installation stage will be processed.

    Args:
        opts: installation options

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    if not WAF.exists():
        err('unable to install package; waf is not installed')
        return False

    # default definitions
    waf_defs = {
    }
    if opts.install_defs:
        waf_defs.update(expand(opts.install_defs))

    # default options
    waf_opts = {
    }
    if opts.install_opts:
        waf_opts.update(expand(opts.install_opts))

    # argument building
    waf_args = [
        'install',
    ]
    waf_args.extend(prepare_definitions(waf_defs))
    waf_args.extend(prepare_arguments(waf_opts))

    # default environment
    env = {
    }
    if opts.install_env:
        env.update(expand(opts.install_env))

    # install to each destination
    for dest_dir in opts.dest_dirs:
        env['DESTDIR'] = dest_dir
        waf_args_tmp = waf_args
        waf_args_tmp.extend(['--destdir', dest_dir])
        if not WAF.execute(waf_args, env=env):
            err('failed to install waf project: {}', opts.name)
            return False

    return True
