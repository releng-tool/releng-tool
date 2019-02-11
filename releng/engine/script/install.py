#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ...util.log import *
from runpy import run_path
import os

#: filename of the script to execute the installation operation (if any)
INSTALL_SCRIPT = 'install'

def install(opts):
    """
    support installation project-defined scripts

    With provided installation options (``RelengInstallOptions``), the
    installation stage will be processed.

    Args:
        opts: installation options

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    assert opts
    def_dir = opts.def_dir
    env = opts.env

    install_script_filename = '{}-{}'.format(opts.name, INSTALL_SCRIPT)
    install_script = os.path.join(def_dir, install_script_filename)
    if not os.path.isfile(install_script):
        return True

    try:
        run_path(install_script, init_globals=env)

        verbose('install script executed: ' + install_script)
    except Exception as e:
        err('error running install script: ' + install_script)
        err('    {}'.format(e))
        return False

    return True
