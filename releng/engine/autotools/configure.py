#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

from ...tool.autoreconf import *
from ...util.io import execute
from ...util.io import prepare_arguments
from ...util.io import prepare_definitions
from ...util.log import *
from ...util.string import expand as EXP

def configure(opts):
    """
    support configuration for autotools projects

    With provided configuration options (``RelengConfigureOptions``), the
    configuration stage will be processed.

    Args:
        opts: configuration options

    Returns:
        ``True`` if the configuration stage is completed; ``False`` otherwise
    """

    # check if autoreconf
    if opts._autotools_autoreconf:
        verbose('configured to run autoreconf')
        if not AUTORECONF.exists():
            err('unable to configure package; autoreconf is not installed')
            return False

        if not AUTORECONF.execute(['--verbose']):
            err('failed to prepare autotools project (autoreconf): {}',
                opts.name)
            return False

    # definitions
    autotoolsDefs = {
        '--prefix': opts.prefix,
        '--exec-prefix': opts.prefix,
    }
    if opts.conf_defs:
        autotoolsDefs.update(EXP(opts.conf_defs))

    # default options
    autotoolsOpts = {
    }
    if opts.conf_opts:
        autotoolsOpts.update(EXP(opts.conf_opts))

    # argument building
    autotoolsArgs = [
    ]
    autotoolsArgs.extend(prepare_definitions(autotoolsDefs))
    autotoolsArgs.extend(prepare_arguments(autotoolsOpts))

    if not execute(['./configure'] + autotoolsArgs,
            env_update=EXP(opts.conf_env), critical=False):
        err('failed to prepare autotools project (configure): {}', opts.name)
        return False

    return True
