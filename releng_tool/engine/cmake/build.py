# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.cmake import CMAKE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def build(opts):
    """
    support building cmake projects

    With provided build options (``RelengBuildOptions``), the build stage will
    be processed.

    Args:
        opts: build options

    Returns:
        ``True`` if the building stage is completed; ``False`` otherwise
    """

    if not CMAKE.exists():
        err('unable to build package; cmake is not installed')
        return False

    # definitions
    cmake_defs = {
    }
    if opts.build_defs:
        cmake_defs.update(expand(opts.build_defs))

    # options
    cmake_opts = {
        '--config': opts._cmake_build_type,
    }
    if opts.build_opts:
        cmake_opts.update(expand(opts.build_opts))

    # argument building
    cmake_args = [
        # tell cmake to invoke build process in the output directory
        '--build',
        opts.build_output_dir,
    ]
    cmake_args.extend(prepare_definitions(cmake_defs, '-D'))
    cmake_args.extend(prepare_arguments(cmake_opts))

    # default environment
    env = {
    }
    if opts.build_env:
        env.update(expand(opts.build_env))

    # enable specific number of parallel jobs is set
    if opts.jobsconf != 1 and opts.jobs > 1:
        env['CMAKE_BUILD_PARALLEL_LEVEL'] = str(opts.jobs)

    if not CMAKE.execute(cmake_args, env=env):
        err('failed to build cmake project: {}', opts.name)
        return False

    return True
