#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ...tool.cmake import *
from ...util.log import *
from ...util.string import expand as EXP

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

    # default options
    cmakeOpts = {
        # build RelWithDebInfo (when using multi-configuration projects)
        '--config': 'RelWithDebInfo',
    }

    # apply package-specific options
    if opts._cmake_opts:
        cmakeOpts.update(EXP(opts._cmake_opts))

    # argument building
    cmakeArgs = [
        # tell cmake to invoke build process in the output directory
        '--build',
        opts.build_output_dir,
    ]

    for key, val in cmakeOpts.items():
        if val:
            cmakeArgs.append('{}={}'.format(key, val))
        else:
            cmakeArgs.append(key)

    # enable specific number of parallel jobs is set
    #
    # https://cmake.org/cmake/help/v3.12/manual/cmake.1.html#build-tool-mode
    if opts.jobsconf != 1:
        cmakeArgs.append('--parallel')
        if opts.jobsconf > 0:
            cmakeArgs.append(str(opts.jobs))

    if not CMAKE.execute(cmakeArgs, env=EXP(opts._cmake_env)):
        err('failed to build cmake project: {}', opts.name)
        return False

    return True
