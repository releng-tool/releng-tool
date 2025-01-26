# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.make import MAKE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def build(opts):
    """
    support building make projects

    With provided build options (``RelengBuildOptions``), the build stage will
    be processed.

    Args:
        opts: build options

    Returns:
        ``True`` if the building stage is completed; ``False`` otherwise
    """

    if not MAKE.exists():
        err('unable to build package; make is not installed')
        return False

    # definitions
    make_defs = {
    }
    if opts.build_defs:
        make_defs.update(expand(opts.build_defs))

    # default options
    make_opts = {
    }
    if opts.build_opts:
        make_opts.update(expand(opts.build_opts))

    # argument building
    make_args = [
    ]
    make_args.extend(prepare_definitions(make_defs))
    make_args.extend(prepare_arguments(make_opts))

    if opts.jobs > 1:
        make_args.append('--jobs')
        make_args.append(str(opts.jobs))

    if not MAKE.execute(make_args, env=expand(opts.build_env)):
        err('failed to build make project: {}', opts.name)
        return False

    return True
