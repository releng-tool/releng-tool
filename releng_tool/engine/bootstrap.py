# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io import run_script
from releng_tool.util.io_opt_file import opt_file
from releng_tool.util.io_wd import wd
from releng_tool.util.log import note
from releng_tool.util.log import verbose
import os

#: filename of the script to execute the bootstrapping operation (if any)
BOOTSTRAP_SCRIPT = 'bootstrap'


def stage(engine, pkg, script_env):  # noqa: ARG001
    """
    handles the bootstrapping stage for a package

    With a provided engine and package instance, the bootstrapping stage will
    be processed. This stage is typically not advertised and is for advanced
    cases where a developer wishes to manipulate their build environment before
    package has started its configuration+ phases.

    Args:
        engine: the engine
        pkg: the package being built
        script_env: script environment information

    Returns:
        ``True`` if the bootstrapping stage is completed; ``False`` otherwise
    """

    verbose('bootstrapping {} (pre-check)...', pkg.name)

    bootstrap_script_filename = f'{pkg.name}-{BOOTSTRAP_SCRIPT}'
    bootstrap_script = os.path.join(pkg.def_dir, bootstrap_script_filename)
    bootstrap_script, bootstrap_script_exists = opt_file(bootstrap_script)
    if not bootstrap_script_exists:
        return True

    note('bootstrapping {}...', pkg.name)

    if pkg.build_subdir:
        build_dir = pkg.build_subdir
    else:
        build_dir = pkg.build_dir

    with wd(build_dir):
        if not run_script(bootstrap_script, script_env, subject='bootstrap'):
            return False

    verbose('bootstrap script executed: ' + bootstrap_script)
    return True
