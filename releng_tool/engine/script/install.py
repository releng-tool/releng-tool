# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.util.io import opt_file
from releng_tool.util.io import run_script
from releng_tool.util.log import verbose
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
    install_script, install_script_exists = opt_file(install_script)
    if not install_script_exists:
        return True

    if not run_script(install_script, env, subject='install'):
        return False

    verbose('install script executed: ' + install_script)
    return True
