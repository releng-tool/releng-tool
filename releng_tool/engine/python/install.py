# -*- coding: utf-8 -*-
# Copyright 2018-2020 releng-tool

from ...tool.python import PYTHON
from ...tool.python import PYTHON_EXTEND_ENV
from ...tool.python import PythonTool
from ...util.io import prepare_arguments
from ...util.io import prepare_definitions
from ...util.log import err
from ...util.string import expand
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
        python_tool = PythonTool(opts._python_interpreter,
            env_include=PYTHON_EXTEND_ENV)
    else:
        python_tool = PYTHON

    if not python_tool.exists():
        err('unable to install package; python is not installed')
        return False

    # definitions
    python_defs = {
        '--prefix': opts.prefix,
    }
    if opts.install_defs:
        python_defs.update(expand(opts.install_defs))

    # always remove the prefix value if:
    #  - *nix: setup.py may ignore provided `--root` value with an "/" prefix
    #  - win32: does not use the prefix value
    if python_defs['--prefix'] == '/' or sys.platform == 'win32':
        del python_defs['--prefix']

    # default options
    python_opts = {
    }
    if opts.install_opts:
        python_opts.update(expand(opts.install_opts))

    # argument building
    python_args = [
        'setup.py',
        # ignore user's pydistutils.cfg
        '--no-user-cfg',
        # invoke the install operation
        'install',
        # avoid building pyc files
        '--no-compile',
    ]
    python_args.extend(prepare_definitions(python_defs))
    python_args.extend(prepare_arguments(python_opts))

    # install to target destination(s)
    #
    # If the package already defines a root path, use it over any other
    # configured destination directories.
    env = expand(opts.install_env)
    if '--root' in python_opts:
        if not python_tool.execute(python_args, env=env):
            err('failed to install python project: {}', opts.name)
            return False
    else:
        # install to each destination
        for dest_dir in opts.dest_dirs:
            if not python_tool.execute(python_args + ['--root', dest_dir],
                    env=env):
                err('failed to install python project: {}', opts.name)
                return False

    return True
