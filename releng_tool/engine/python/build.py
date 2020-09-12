#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

from ...tool.python import *
from ...util.io import prepare_arguments
from ...util.io import prepare_definitions
from ...util.log import *
from ...util.string import expand as EXP

def build(opts):
    """
    support building python projects

    With provided build options (``RelengBuildOptions``), the build stage will
    be processed.

    Args:
        opts: build options

    Returns:
        ``True`` if the building stage is completed; ``False`` otherwise
    """

    if opts._python_interpreter:
        pythonTool = PythonTool(opts._python_interpreter,
            env_include=PYTHON_EXTEND_ENV)
    else:
        pythonTool = PYTHON

    if not pythonTool.exists():
        err('unable to build package; python is not installed')
        return False

    # definitions
    pythonDefs = {
    }
    if opts.build_defs:
        pythonDefs.update(EXP(opts.build_defs))

    # default options
    pythonOpts = {
    }
    if opts.build_opts:
        pythonOpts.update(EXP(opts.build_opts))

    # default environment
    pythonPath1 = pythonTool.path(sysroot=opts.staging_dir, prefix=opts.prefix)
    pythonPath2 = pythonTool.path(sysroot=opts.target_dir, prefix=opts.prefix)
    env = {
        'PYTHONPATH': pythonPath1 + os.pathsep + pythonPath2
    }

    # apply package-specific environment options
    if opts.build_env:
        env.update(EXP(opts.build_env))

    # argument building
    pythonArgs = [
        'setup.py',
        # ignore user's pydistutils.cfg
        '--no-user-cfg',
        # invoke the build operation
        'build',
    ]
    pythonArgs.extend(prepare_definitions(pythonDefs))
    pythonArgs.extend(prepare_arguments(pythonOpts))

    if not pythonTool.execute(pythonArgs, env=env):
        err('failed to build python project: {}', opts.name)
        return False

    return True
