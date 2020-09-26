# -*- coding: utf-8 -*-
# Copyright 2018-2020 releng-tool

from ...util.log import *
from ...util.io import opt_file
from ...util.io import run_script
import os

#: filename of the script to execute the building operation (if any)
BUILD_SCRIPT = 'build'

def build(opts):
    """
    support building project-defined scripts

    With provided build options (``RelengBuildOptions``), the build stage will
    be processed.

    Args:
        opts: build options

    Returns:
        ``True`` if the building stage is completed; ``False`` otherwise
    """

    assert opts
    def_dir = opts.def_dir
    env = opts.env

    build_script_filename = '{}-{}'.format(opts.name, BUILD_SCRIPT)
    build_script = os.path.join(def_dir, build_script_filename)
    build_script, build_script_exists = opt_file(build_script)
    if not build_script_exists:
        return True

    if not run_script(build_script, env, subject='build'):
        return False

    verbose('install script executed: ' + build_script)
    return True
