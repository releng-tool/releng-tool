# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.make import MAKE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def install(opts):
    """
    support installation make projects

    With provided installation options (``RelengInstallOptions``), the
    installation stage will be processed.

    Args:
        opts: installation options

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    if not MAKE.exists():
        err('unable to install package; make is not installed')
        return False

    # definitions
    make_defs = {
        'PREFIX': opts.prefix,
    }
    if opts.install_defs:
        make_defs.update(expand(opts.install_defs))

    # default options
    make_opts = {
    }
    if opts.install_opts:
        make_opts.update(expand(opts.install_opts))

    # argument building
    make_args = [
    ]

    # If the provided package has not provided any installation options,
    # indicate that the install target will be run.
    if not opts.install_opts:
        make_args.append('install')

    make_args.extend(prepare_definitions(make_defs))
    make_args.extend(prepare_arguments(make_opts))

    # prepare environment for installation request; an environment dictionary is
    # always needed to apply a custom DESTDIR during each install request
    env = expand(opts.install_env)
    if not env:
        env = {}

    # install to each destination
    for dest_dir in opts.dest_dirs:
        env['DESTDIR'] = dest_dir
        make_args_tmp = ['DESTDIR=' + dest_dir, *make_args]
        if not MAKE.execute(make_args_tmp, env=env):
            err('failed to install make project: {}', opts.name)
            return False

    return True
