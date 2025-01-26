# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.make import MAKE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def install(opts):
    """
    support installation autotools projects

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
    autotools_defs = {
    }
    if opts.install_defs:
        autotools_defs.update(expand(opts.install_defs))

    # default options
    autotools_opts = {
    }
    if opts.install_opts:
        autotools_opts.update(expand(opts.install_opts))

    # argument building
    autotools_args = [
    ]

    # If the provided package has not provided any installation options,
    # indicate that the install target will be run.
    if not opts.install_opts:
        autotools_args.append('install')

    autotools_args.extend(prepare_definitions(autotools_defs))
    autotools_args.extend(prepare_arguments(autotools_opts))

    # install to each destination
    env = expand(opts.install_env)
    for dest_dir in opts.dest_dirs:
        if not MAKE.execute(['DESTDIR=' + dest_dir, *autotools_args], env=env):
            err('failed to install autotools project: {}', opts.name)
            return False

    return True
