# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from glob import glob
from releng_tool.defs import VcsType
from releng_tool.tool.patch import PATCH
from releng_tool.util.io import run_script
from releng_tool.util.io_opt_file import opt_file
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.log import verbose
import os
import re


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

    # check if we know we do not want to attempt patching for this package
    #
    # Typically, patches apply to only regular packages not in a development
    # mode. However, there are various configuration types that can skip
    # patches when in a regular mode or even apply patches in a development
    # mode. To start off, we know we can immediately skip the patch phase if:
    #  - In a regular mode and a package explicitly indicates not to patch.
    #  - In a development mode, but no development patch configuration exists.
    if not pkg.devmode and pkg.ignore_patches is True:
        return True

    if pkg.devmode and not pkg.devmode_patches:
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

        # we have packages -- also make sure there is no special patch
        # configuration which filters out/ignores these patches for this
        # runtime state
        patterns = None
        add_matched_patches = True
        filtered_patches = []

        if not pkg.devmode and pkg.ignore_patches:
            patterns = re.compile('|'.join(pkg.ignore_patches))
            add_matched_patches = False
        elif pkg.devmode and pkg.devmode_patches is not True:
            if isinstance(pkg.devmode_patches, dict):
                ipcfg = pkg.devmode_patches.get(engine.opts.devmode)
                if ipcfg is True:
                    filtered_patches = patches
                elif ipcfg:
                    patterns = re.compile('|'.join(ipcfg))
            else:
                patterns = re.compile('|'.join(pkg.devmode_patches))
        else:
            filtered_patches = patches

        # filter out any patches not applicable
        if patterns:
            debug(f'patch filter patterns: {patterns}')
            for patch in patches:
                patch_fname = os.path.basename(patch)
                if bool(patterns.search(patch_fname)) == add_matched_patches:
                    filtered_patches.append(patch)

        # if any patches have been filtered, debug log this
        if filtered_patches != patches:
            debug('detected patches:')
            for patch in sorted(patches):
                debug(f' - {patch}')
            debug('filtered patches:')
            for patch in sorted(filtered_patches):
                debug(f' - {patch}')
            if not filtered_patches:
                debug('(none)')

        # no applicable patches, no-op patch stage -- return
        patches = filtered_patches
        if not patches:
            debug('no patches detected after filtering')
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
        '--forward',
        '--ignore-whitespace',
        '--strip=1',
    ]

    # forcing verbose mode as a hack for patch compatibility
    #
    # It has been observed for select environments that running in a verbose
    # mode can alter the ability to apply a patch successfully. Specifically,
    # running with patch 2.5.9 built for Strawberry Perl will sometimes
    # report hunk failures (code 3). However, when running in a verbose mode,
    # patches look to apply. Using `--verbose` for all environments does
    # not have any issues, to always use it to be flexible for this odd use
    # case.
    if 'releng.disable_verbose_patch' not in engine.opts.quirks:
        patch_args.append('--verbose')

    for patch in patches:
        log(f'({os.path.basename(patch)})')

        patch_out = []
        if not PATCH.execute([*patch_args, f'--input={patch}'],
                cwd=patch_dir, capture=patch_out):
            log('\n'.join(patch_out))
            err('failed to apply patch')
            return False

    return True
