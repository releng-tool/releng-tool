# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.engine.script import resolve_remote_script
from releng_tool.util.io import run_script
from releng_tool.util.io_opt_file import opt_file
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
    build_dir = opts.build_dir
    def_dir = opts.def_dir
    env = opts.env

    install_script_filename = f'{opts.name}-{INSTALL_SCRIPT}'
    install_script = os.path.join(def_dir, install_script_filename)
    install_script, install_script_exists = opt_file(install_script)
    if not install_script_exists:
        if (not opts._remote_scripts or
                'releng.disable_remote_scripts' in opts._quirks):
            return True

        install_script, install_script_exists = \
            resolve_remote_script(build_dir, INSTALL_SCRIPT)
        if not install_script_exists:
            return True

    if not run_script(install_script, env, subject='install'):
        return False

    verbose('install script executed: ' + install_script)
    return True
