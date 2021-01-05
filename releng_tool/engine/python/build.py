# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.tool.python import PYTHON
from releng_tool.tool.python import PYTHON_EXTEND_ENV
from releng_tool.tool.python import PythonTool
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand
import os

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
        python_tool = PythonTool(opts._python_interpreter,
            env_include=PYTHON_EXTEND_ENV)
    else:
        python_tool = PYTHON

    if not python_tool.exists():
        err('unable to build package; python is not installed')
        return False

    # definitions
    python_defs = {
    }
    if opts.build_defs:
        python_defs.update(expand(opts.build_defs))

    # default options
    python_opts = {
    }
    if opts.build_opts:
        python_opts.update(expand(opts.build_opts))

    # default environment
    python_path1 = python_tool.path(sysroot=opts.staging_dir, prefix=opts.prefix)
    python_path2 = python_tool.path(sysroot=opts.target_dir, prefix=opts.prefix)
    env = {
        'PYTHONPATH': python_path1 + os.pathsep + python_path2
    }

    # apply package-specific environment options
    if opts.build_env:
        env.update(expand(opts.build_env))

    # argument building
    python_args = [
        'setup.py',
        # ignore user's pydistutils.cfg
        '--no-user-cfg',
        # invoke the build operation
        'build',
    ]
    python_args.extend(prepare_definitions(python_defs))
    python_args.extend(prepare_arguments(python_opts))

    if not python_tool.execute(python_args, env=env):
        err('failed to build python project: {}', opts.name)
        return False

    return True
