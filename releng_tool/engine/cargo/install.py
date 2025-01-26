# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.engine.cargo import CARGO_COMMON_TARGET
from releng_tool.tool.cargo import CARGO
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand
import os


def install(opts):
    """
    support installation cargo projects

    With provided installation options (``RelengInstallOptions``), the
    installation stage will be processed.

    Args:
        opts: installation options

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    if not CARGO.exists():
        err('unable to install package; cargo is not installed')
        return False

    # default definitions
    cargo_defs = {
    }
    if opts.install_defs:
        cargo_defs.update(expand(opts.install_defs))

    # default options
    cargo_opts = {
    }
    if opts.install_opts:
        cargo_opts.update(expand(opts.install_opts))

    # argument building
    cargo_args = [
        'install',
        # controlled dependencies
        '--locked',
        # allow overwrites
        '--force',
        # avoid generating tracking information
        '--no-track',
        # never perform online interaction in install stage
        '--offline',
        # reference the package's output folder where the build was performed
        '--target-dir',
        os.path.join(opts.build_base_dir, CARGO_COMMON_TARGET),
        # configure a path at the base of the root (see also `--root` below)
        '--path',
        '.',
    ]
    cargo_args.extend(opts._cargo_depargs)

    cargo_args.extend(prepare_definitions(cargo_defs))
    cargo_args.extend(prepare_arguments(cargo_opts))

    # default environment
    env = {
    }
    if opts.install_env:
        env.update(expand(opts.install_env))

    # install to target destination(s)
    #
    # If the package already defines a destination directory, use it over
    # any other configured destination directories.
    if '--root' in cargo_args:
        if not CARGO.execute(cargo_args, env=env):
            err('failed to install cargo project: {}', opts.name)
            return False
    else:
        # install to each destination
        for dest_dir in opts.dest_dirs:
            prefixed_dest_dir = dest_dir + opts.prefix
            cargo_args_tmp = [
                *cargo_args,
                '--root',
                prefixed_dest_dir,
            ]
            if not CARGO.execute(cargo_args_tmp, env=env):
                err('failed to install cargo project: {}', opts.name)
                return False

    return True
