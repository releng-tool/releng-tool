#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ...tool.autoreconf import *
from ...util.io import execute
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

    # default options
    autotoolsOpts = {
        '--prefix': opts.prefix,
        '--exec-prefix': opts.prefix,
    }

    # apply package-specific options
    if opts._autotools_conf_opts:
        autotoolsOpts.update(EXP(opts._autotools_conf_opts))

    # argument building
    autotoolsArgs = [
    ]

    for key, val in autotoolsOpts.items():
        if val:
            autotoolsArgs.append('{}={}'.format(key, val))
        else:
            autotoolsArgs.append(key)

    if not execute(['./configure'] + autotoolsArgs,
            env_update=EXP(opts._autotools_conf_env), critical=False):
        err('failed to prepare autotools project (configure): {}', opts.name)
        return False

    return True
