# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.xmake import XMAKE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def build(opts):
    """
    support building xmake projects

    With provided build options (``RelengBuildOptions``), the build stage will
    be processed.

    Args:
        opts: build options

    Returns:
        ``True`` if the building stage is completed; ``False`` otherwise
    """

    if not XMAKE.exists():
        err('unable to build package; xmake is not installed')
        return False

    # definitions
    xmake_defs = {
    }
    if opts.build_defs:
        xmake_defs.update(expand(opts.build_defs))

    # options
    xmake_opts = {
    }
    if opts.build_opts:
        xmake_opts.update(expand(opts.build_opts))

    # argument building
    xmake_args = [
        'build',
    ]
    xmake_args.extend(prepare_definitions(xmake_defs))
    xmake_args.extend(prepare_arguments(xmake_opts))

    if opts.jobs > 1:
        xmake_args.append(f'--jobs={opts.jobs}')

    # default environment
    env = {
        'XMAKE_CONFIGDIR': opts.build_output_dir,
        'XMAKE_GLOBALDIR': f'{opts.build_base_dir}/.releng-tool-xmake-global',
    }
    if opts.build_env:
        env.update(expand(opts.build_env))

    if not XMAKE.execute(xmake_args, env=env):
        err('failed to build xmake project: {}', opts.name)
        return False

    return True
