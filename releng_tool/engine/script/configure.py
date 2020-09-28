# -*- coding: utf-8 -*-
# Copyright 2018-2020 releng-tool

from ...util.log import verbose
from ...util.io import opt_file
from ...util.io import run_script
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
    configure_script, configure_script_exists = opt_file(configure_script)
    if not configure_script_exists:
        return True

    if not run_script(configure_script, env, subject='configure'):
        return False

    verbose('install script executed: ' + configure_script)
    return True
