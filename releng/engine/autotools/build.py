#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ...tool.make import *
from ...util.io import prepare_arguments
from ...util.log import *
from ...util.string import expand as EXP

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

    # default options
    autotoolsOpts = {
    }

    # apply package-specific options
    if opts._autotools_opts:
        autotoolsOpts.update(EXP(opts._autotools_opts))

    # argument building
    autotoolsArgs = [
    ]
    autotoolsArgs.extend(prepare_arguments(autotoolsOpts))

    if opts.jobs > 1:
        autotoolsArgs.append('--jobs')
        autotoolsArgs.append(str(opts.jobs))

    if not MAKE.execute(autotoolsArgs, env=EXP(opts._autotools_env)):
        err('failed to build autotools project: {}', opts.name)
        return False

    return True
