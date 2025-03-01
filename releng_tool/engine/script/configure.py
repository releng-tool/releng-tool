# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.engine.script import resolve_remote_script
from releng_tool.util.io import run_script
from releng_tool.util.io_opt_file import opt_file
from releng_tool.util.log import verbose
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
    build_dir = opts.build_dir
    def_dir = opts.def_dir
    env = opts.env

    configure_script_filename = f'{opts.name}-{CONFIGURE_SCRIPT}'
    configure_script = os.path.join(def_dir, configure_script_filename)
    configure_script, configure_script_exists = opt_file(configure_script)
    if not configure_script_exists:
        if (not opts._remote_scripts or
                'releng.disable_remote_scripts' in opts._quirks):
            return True

        configure_script, configure_script_exists = \
            resolve_remote_script(build_dir, CONFIGURE_SCRIPT)
        if not configure_script_exists:
            return True

    if not run_script(configure_script, env, subject='configure'):
        return False

    verbose('install script executed: ' + configure_script)
    return True
