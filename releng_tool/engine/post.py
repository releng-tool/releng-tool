# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io import run_script
from releng_tool.util.io_opt_file import opt_file
from releng_tool.util.io_wd import wd
from releng_tool.util.log import note
from releng_tool.util.log import verbose
import os


#: filename of the script to execute the post-processing operation (if any)
POST_SCRIPT = 'post'


def stage(engine, pkg, script_env):  # noqa: ARG001
    """
    handles the post-processing stage for a package

    With a provided engine and package instance, the post-processing stage will
    be processed. This stage is typically not advertised and is for advanced
    cases where a developer wishes to manipulate their build environment after
    package has completed each of its phases.

    Args:
        engine: the engine
        pkg: the package being built
        script_env: script environment information

    Returns:
        ``True`` if the post-processing stage is completed; ``False`` otherwise
    """

    verbose('post-processing {} (pre-check)...', pkg.name)

    post_script_filename = f'{pkg.name}-{POST_SCRIPT}'
    post_script = os.path.join(pkg.def_dir, post_script_filename)
    post_script, post_script_exists = opt_file(post_script)
    if not post_script_exists:
        return True

    note('post-processing {}...', pkg.name)

    if pkg.build_subdir:
        build_dir = pkg.build_subdir
    else:
        build_dir = pkg.build_dir

    with wd(build_dir):
        if not run_script(post_script, script_env, subject='post-processing'):
            return False

    verbose('post-processing script executed: ' + post_script)
    return True
