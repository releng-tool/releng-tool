# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

from ...tool.python import *
from ...util.io import prepare_arguments
from ...util.io import prepare_definitions
from ...util.log import *
from ...util.string import expand

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
