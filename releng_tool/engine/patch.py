# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from glob import glob
from releng_tool.defs import VcsType
from releng_tool.tool.patch import PATCH
from releng_tool.util.io import run_script
from releng_tool.util.io_opt_file import opt_file
from releng_tool.util.log import err
from releng_tool.util.log import note
from releng_tool.util.log import verbose
import os


#: filename of the script to execute custom patching operations (if any)
PATCH_SCRIPT = 'patch'


def stage(engine, pkg, script_env):
    """
    handles the patching stage for a package

    With a provided engine and package instance, the patching stage will be
    processed.

    Args:
        engine: the engine
        pkg: the package being patched
        script_env: script environment information

    Returns:
        ``True`` if the patching stage is completed; ``False`` otherwise
    """

    # local-vcs-type packages do not need to patch
    if pkg.vcs_type is VcsType.LOCAL:
        return True

    # internal packages flagged for local sources do not have a patch stage
    if pkg.is_internal and pkg.local_srcs:
        return True

    # packages which have a custom revision while in development mode will
    # not perform the patch stage
    if pkg.devmode:
        return True

    verbose('patching {} (pre-check)...', pkg.name)

    # check if we have a patch script override to process (instead of
    # patch files)
    patch_script_filename = f'{pkg.name}-{PATCH_SCRIPT}'
    patch_script_base = os.path.join(pkg.def_dir, patch_script_filename)
    patch_script, has_patch_script = opt_file(patch_script_base)

    # if not patch script, check if we detect any patch files in the
    # package's folder
    patches = None
    if not has_patch_script:
        patch_glob = os.path.join(pkg.def_dir, '*.patch')
        patches = glob(patch_glob)

        # no patch script or patches, no-op patch stage -- return
        if not patches:
            return True

    note('patching {}...', pkg.name)

    if pkg.patch_subdir:
        patch_dir = pkg.patch_subdir
    else:
        patch_dir = pkg.build_dir

    # if we have a patch script, run it
    if has_patch_script:
        if not run_script(patch_script, script_env, subject='patch'):
            return False

        verbose('patch script executed: ' + patch_script)
        return True

    # for the found patches, sort and apply each
    patches = sorted(patches)
    if not PATCH.exists():
        err('unable to apply patches; patch is not installed')
        return False

    patch_args = [
        '--batch',
        '--binary',
        '--forward',
        '--ignore-whitespace',
        '--strip=1',
    ]

    # attempt to be flexible for patches between cross-platform environments
    # by disabling the heuristic for transforming line endings
    if 'releng.disable_binary_patch' not in engine.opts.quirks:
        patch_args.append('--binary')

    for patch in patches:
        print(f'({os.path.basename(patch)})')

        if not PATCH.execute([*patch_args, f'--input={patch}'], cwd=patch_dir):
            err('failed to apply patch')
            return False

    return True
