#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

from ...defs import PackageInstallType
from ...tool.make import *
from ...util.io import prepare_arguments
from ...util.io import prepare_definitions
from ...util.log import *
from ...util.string import expand as EXP

def install(opts):
    """
    support installation autotools projects

    With provided installation options (``RelengInstallOptions``), the
    installation stage will be processed.

    Args:
        opts: installation options

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    if not MAKE.exists():
        err('unable to install package; make is not installed')
        return False

    # definitions
    autotoolsDefs = {
    }
    if opts.install_defs:
        autotoolsDefs.update(EXP(opts.install_defs))

    # default options
    autotoolsOpts = {
    }
    if opts.install_opts:
        autotoolsOpts.update(EXP(opts.install_opts))

    # argument building
    autotoolsArgs = [
    ]

    # If the provided package has not provided any installation options,
    # indicate that the install target will be run.
    if not opts.install_opts:
        autotoolsArgs.append('install')

    autotoolsArgs.extend(prepare_definitions(autotoolsDefs))
    autotoolsArgs.extend(prepare_arguments(autotoolsOpts))

    # install to each destination
    env = EXP(opts.install_env)
    for dest_dir in opts.dest_dirs:
        if not MAKE.execute(['DESTDIR=' + dest_dir] + autotoolsArgs, env=env):
            err('failed to install autotools project: {}', opts.name)
            return False

    return True
