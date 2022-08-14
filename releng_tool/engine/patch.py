# -*- coding: utf-8 -*-
# Copyright 2018-2022 releng-tool

from glob import glob
from releng_tool.defs import VcsType
from releng_tool.tool.patch import PATCH
from releng_tool.util.log import err
from releng_tool.util.log import note
from releng_tool.util.log import verbose
from runpy import run_path
import os
import sys

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

    note('patching {}...', pkg.name)
    sys.stdout.flush()

    if pkg.build_subdir:
        build_dir = pkg.build_subdir
    else:
        build_dir = pkg.build_dir

    patch_script_filename = '{}-{}'.format(pkg.name, PATCH_SCRIPT)
    patch_script = os.path.join(pkg.def_dir, patch_script_filename)
    if os.path.isfile(patch_script):
        try:
            run_path(patch_script, init_globals=script_env)

            verbose('patch script executed: ' + patch_script)
        except Exception as e:
            err('error running patch script: \n'
                '    {}', patch_script, e)
            return False

    # find all patches in the package's folder, sort and apply each
    patch_glob = os.path.join(pkg.def_dir, '*.patch')
    patches = glob(patch_glob)
    if patches:
        patches = sorted(patches)
        if not PATCH.exists():
            err('unable to apply patches; patch is not installed')
            return False

        for patch in patches:
            print('({})'.format(os.path.basename(patch)))

            if not PATCH.execute([
                    '--batch',
                    '--forward',
                    '--ignore-whitespace',
                    '--input={}'.format(patch),
                    '--strip=1',
                    ], cwd=build_dir):
                err('failed to apply patch')
                return False

    return True
