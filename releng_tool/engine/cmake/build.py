# -*- coding: utf-8 -*-
# Copyright 2018-2020 releng-tool

from ...tool.cmake import CMAKE
from ...util.io import prepare_arguments
from ...util.io import prepare_definitions
from ...util.log import err
from ...util.log import verbose
from ...util.string import expand

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
        # build RelWithDebInfo (when using multi-configuration projects)
        '--config': 'RelWithDebInfo',
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

    # enable specific number of parallel jobs is set
    #
    # https://cmake.org/cmake/help/v3.12/manual/cmake.1.html#build-tool-mode
    if 'releng.cmake.disable_parallel_option' not in opts._quirks:
        if opts.jobsconf != 1:
            cmake_args.append('--parallel')
            if opts.jobsconf > 0:
                cmake_args.append(str(opts.jobs))
    else:
        verbose('cmake parallel jobs disabled by quirk')

    if not CMAKE.execute(cmake_args, env=expand(opts.build_env)):
        err('failed to build cmake project: {}', opts.name)
        return False

    return True
