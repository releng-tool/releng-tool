#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ...util.log import *
from runpy import run_path
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
    script_env = opts.env

    build_script_filename = '{}-{}'.format(opts.name, BUILD_SCRIPT)
    build_script = os.path.join(def_dir, build_script_filename)
    if not os.path.isfile(build_script):
        return True

    try:
        run_path(build_script, init_globals=script_env)

        verbose('build script executed: ' + build_script)
    except Exception as e:
        err('error running build script: ' + build_script)
        err('    {}'.format(e))
        return False

    return True
