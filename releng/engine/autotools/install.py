#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ...defs import PackageInstallType
from ...tool.make import *
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

    # default options
    autotoolsOpts = {
    }

    # apply package-specific options
    if opts._autotools_install_opts:
        autotoolsOpts.update(EXP(opts._autotools_install_opts))

    # argument building
    makeArgs = [
    ]

    # If the provided package has not provided any installation options,
    # indicate that the install target will be run.
    if not opts._autotools_install_opts:
        makeArgs.append('install')

    for key, val in autotoolsOpts.items():
        if val:
            makeArgs.append('{}={}'.format(key, val))
        else:
            makeArgs.append(key)

    # install to each destination
    env = EXP(opts._autotools_install_env)
    for dest_dir in opts.dest_dirs:
        if not MAKE.execute(['DESTDIR=' + dest_dir] + makeArgs, env=env):
            err('failed to install autotools project: {}', opts.name)
            return False

    return True
