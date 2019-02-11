#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ...util.log import *
from runpy import run_path
import os

#: filename of the script to execute the configuration operation (if any)
CONFIGURE_SCRIPT = 'configure'

def configure(opts):
    """
    support configuration project-defined scripts

    With provided configuration options (``RelengConfigureOptions``), the
    configuration stage will be processed.

    Args:
        opts: configuration options

    Returns:
        ``True`` if the configuration stage is completed; ``False`` otherwise
    """

    assert opts
    def_dir = opts.def_dir
    env = opts.env

    configure_script_filename = '{}-{}'.format(opts.name, CONFIGURE_SCRIPT)
    configure_script = os.path.join(def_dir, configure_script_filename)
    if not os.path.isfile(configure_script):
        return True

    try:
        run_path(configure_script, init_globals=env)

        verbose('configure script executed: ' + configure_script)
    except Exception as e:
        err('error running configure script: ' + configure_script)
        err('    {}'.format(e))
        return False

    return True
