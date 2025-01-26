# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.make import MAKE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def build(opts):
    """
    support building autotools projects

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
    autotools_defs = {
    }
    if opts.build_defs:
        autotools_defs.update(expand(opts.build_defs))

    # default options
    autotools_opts = {
    }
    if opts.build_opts:
        autotools_opts.update(expand(opts.build_opts))

    # argument building
    autotools_args = [
    ]
    autotools_args.extend(prepare_definitions(autotools_defs))
    autotools_args.extend(prepare_arguments(autotools_opts))

    if opts.jobs > 1:
        autotools_args.append('--jobs')
        autotools_args.append(str(opts.jobs))

    if not MAKE.execute(autotools_args, env=expand(opts.build_env)):
        err('failed to build autotools project: {}', opts.name)
        return False

    return True
