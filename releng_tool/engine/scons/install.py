# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.scons import SCONS
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def install(opts):
    """
    support installation scons projects

    With provided installation options (``RelengInstallOptions``), the
    installation stage will be processed.

    Args:
        opts: installation options

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    if not SCONS.exists():
        err('unable to install package; scons is not installed')
        return False

    # definitions
    scons_defs = {
        'PREFIX': opts.prefix,
    }
    if opts.install_defs:
        scons_defs.update(expand(opts.install_defs))

    # default options
    scons_opts = {
        # default quiet
        '-Q': '',
    }
    if opts.install_opts:
        scons_opts.update(expand(opts.install_opts))

    # argument building
    scons_args = [
    ]

    # If the provided package has not provided any installation options,
    # indicate that the install target will be run.
    if not opts.install_opts:
        scons_args.append('install')

    scons_args.extend(prepare_definitions(scons_defs))
    scons_args.extend(prepare_arguments(scons_opts))

    # prepare environment for installation request; an environment dictionary is
    # always needed to apply a custom DESTDIR during each install request
    env = expand(opts.install_env)
    if not env:
        env = {}

    # install to target destination(s)
    #
    # If the package already defines a destination directory, use it over
    # any other configured destination directories.
    if 'DESTDIR' in scons_defs:
        if not SCONS.execute(scons_args, env=env):
            err('failed to install scons project: {}', opts.name)
            return False
    else:
        # install to each destination
        for dest_dir in opts.dest_dirs:
            env['DESTDIR'] = dest_dir
            scons_args_tmp = ['DESTDIR=' + dest_dir, *scons_args]
            if not SCONS.execute(scons_args_tmp, env=env):
                err('failed to install scons project: {}', opts.name)
                return False

    return True
