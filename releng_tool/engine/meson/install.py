# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.meson import MESON
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def install(opts):
    """
    support installation meson projects

    With provided installation options (``RelengInstallOptions``), the
    installation stage will be processed.

    Args:
        opts: installation options

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    if not MESON.exists():
        err('unable to install package; meson is not installed')
        return False

    # default definitions
    meson_defs = {
    }
    if opts.install_defs:
        meson_defs.update(expand(opts.install_defs))

    # default options
    meson_opts = {
    }
    if opts.install_opts:
        meson_opts.update(expand(opts.install_opts))

    # argument building
    meson_args = [
        'install',
        '-C',
        opts.build_output_dir,
        # do not perform a rebuild for this install invoke
        '--no-rebuild',
    ]
    meson_args.extend(prepare_definitions(meson_defs, '-D'))
    meson_args.extend(prepare_arguments(meson_opts))

    # default environment
    env = {
    }
    if opts.install_env:
        env.update(expand(opts.install_env))

    # install to each destination
    for dest_dir in opts.dest_dirs:
        env['DESTDIR'] = dest_dir
        meson_args_tmp = meson_args
        meson_args_tmp.extend(['--destdir', dest_dir])
        if not MESON.execute(meson_args, env=env):
            err('failed to install meson project: {}', opts.name)
            return False

    return True
