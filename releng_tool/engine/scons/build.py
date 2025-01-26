# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.scons import SCONS
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def build(opts):
    """
    support building scons projects

    With provided build options (``RelengBuildOptions``), the build stage will
    be processed.

    Args:
        opts: build options

    Returns:
        ``True`` if the building stage is completed; ``False`` otherwise
    """

    if not SCONS.exists():
        err('unable to build package; scons is not installed')
        return False

    # definitions
    scons_defs = {
    }
    if opts.build_defs:
        scons_defs.update(expand(opts.build_defs))

    # default options
    scons_opts = {
        # default quiet
        '-Q': '',
    }
    if opts.build_opts:
        scons_opts.update(expand(opts.build_opts))

    # argument building
    scons_args = [
    ]
    scons_args.extend(prepare_definitions(scons_defs))
    scons_args.extend(prepare_arguments(scons_opts))

    if opts.jobs > 1:
        scons_args.append(f'--jobs={opts.jobs}')

    if not SCONS.execute(scons_args, env=expand(opts.build_env)):
        err('failed to build scons project: {}', opts.name)
        return False

    return True
