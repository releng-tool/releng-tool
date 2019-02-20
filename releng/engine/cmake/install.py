#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ...tool.cmake import *
from ...util.io import prepare_arguments
from ...util.log import *
from ...util.string import expand as EXP

def install(opts):
    """
    support installation cmake projects

    With provided installation options (``RelengInstallOptions``), the
    installation stage will be processed.

    Args:
        opts: installation options

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    if not CMAKE.exists():
        err('unable to install package; cmake is not installed')
        return False

    # default options
    cmakeOpts = {
        # build RelWithDebInfo (when using multi-configuration projects)
        '--config': 'RelWithDebInfo',
        # default install using the install target
        '--target': 'install',
    }

    # apply package-specific options
    if opts._cmake_install_opts:
        cmakeOpts.update(EXP(opts._cmake_install_opts))

    # argument building
    cmakeArgs = [
        '--build',
        opts.build_output_dir,
    ]
    cmakeArgs.extend(prepare_arguments(cmakeOpts))

    # prepare environment for installation request; an environment dictionary is
    # always needed to apply a custom DESTDIR during each install request
    env = EXP(opts._cmake_install_env)
    if not env:
        env = {}

    # install to each destination
    for dest_dir in opts.dest_dirs:
        env['DESTDIR'] = dest_dir
        if not CMAKE.execute(cmakeArgs, env=env):
            err('failed to install cmake project: {}', opts.name)
            return False

    return True
