# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.engine.meson import meson_prepare_environment
from releng_tool.tool.meson import MESON
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def build(opts):
    """
    support building meson projects

    With provided build options (``RelengBuildOptions``), the build stage will
    be processed.

    Args:
        opts: build options

    Returns:
        ``True`` if the building stage is completed; ``False`` otherwise
    """

    if not MESON.exists():
        err('unable to build package; meson is not installed')
        return False

    # definitions
    meson_defs = {
    }
    if opts.build_defs:
        meson_defs.update(expand(opts.build_defs))

    # options
    meson_opts = {
    }
    if opts.build_opts:
        meson_opts.update(expand(opts.build_opts))

    # environment
    meson_env = meson_prepare_environment(opts)
    if opts.build_env:
        meson_env.update(opts.build_env)

    # argument building
    meson_args = [
        'compile',
        # tell meson to invoke build process in the output directory
        '-C',
        opts.build_output_dir,
    ]
    meson_args.extend(prepare_definitions(meson_defs, '-D'))
    meson_args.extend(prepare_arguments(meson_opts))

    if opts.jobs > 1:
        meson_args.append('--jobs')
        meson_args.append(str(opts.jobs))

    if not MESON.execute(meson_args, env=expand(meson_env)):
        err('failed to build meson project: {}', opts.name)
        return False

    return True
