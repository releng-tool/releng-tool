#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

from ...tool.python import *
from ...util.io import prepare_arguments
from ...util.io import prepare_definitions
from ...util.log import *
from ...util.string import expand as EXP
import sys

def install(opts):
    """
    support installation python projects

    With provided installation options (``RelengInstallOptions``), the
    installation stage will be processed.

    Args:
        opts: installation options

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    if opts._python_interpreter:
        pythonTool = PythonTool(opts._python_interpreter,
            env_include=PYTHON_EXTEND_ENV)
    else:
        pythonTool = PYTHON

    if not pythonTool.exists():
        err('unable to install package; python is not installed')
        return False

    # definitions
    pythonDefs = {
        '--prefix': opts.prefix,
    }
    if opts.install_defs:
        pythonDefs.update(EXP(opts.install_defs))

    # always remove the prefix value if:
    #  - *nix: setup.py may ignore provided `--root` value with an "/" prefix
    #  - win32: does not use the prefix value
    if pythonDefs['--prefix'] == '/' or sys.platform == 'win32':
        del pythonDefs['--prefix']

    # default options
    pythonOpts = {
    }
    if opts.install_opts:
        pythonOpts.update(EXP(opts.install_opts))

    # argument building
    pythonArgs = [
        'setup.py',
        # ignore user's pydistutils.cfg
        '--no-user-cfg',
        # invoke the install operation
        'install',
        # avoid building pyc files
        '--no-compile',
    ]
    pythonArgs.extend(prepare_definitions(pythonDefs))
    pythonArgs.extend(prepare_arguments(pythonOpts))

    # install to target destination(s)
    #
    # If the package already defines a root path, use it over any other
    # configured destination directories.
    env = EXP(opts.install_env)
    if '--root' in pythonOpts:
        if not pythonTool.execute(pythonArgs, env=env):
            err('failed to install python project: {}', opts.name)
            return False
    else:
        # install to each destination
        for dest_dir in opts.dest_dirs:
            if not pythonTool.execute(pythonArgs + ['--root', dest_dir],
                    env=env):
                err('failed to install python project: {}', opts.name)
                return False

    return True
