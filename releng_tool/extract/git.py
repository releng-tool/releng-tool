# -*- coding: utf-8 -*-
# Copyright 2018-2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.packages import pkg_cache_key
from releng_tool.tool.git import GIT
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import warn
import os


def extract(opts):
    """
    support extraction (checkout) of a git cache into a build directory

    With provided extraction options (``RelengExtractOptions``), the extraction
    stage will be processed. A Git extraction process will populate a working
    tree based off the cached Git tree acquired from the fetch stage.

    Args:
        opts: the extraction options

    Returns:
        ``True`` if the extraction stage is completed; ``False`` otherwise
    """

    assert opts
    cache_dir = opts.cache_dir
    revision = opts.revision
    work_dir = opts.work_dir

    if not GIT.exists():
        err('unable to extract package; git is not installed')
        return None

    # extract the package
    if not _workdir_extract(cache_dir, work_dir, revision):
        return False

    # extract submodules (if configured to do so)
    if opts._git_submodules:
        if not _process_submodules(opts, work_dir):
            return False

    return True


def _process_submodules(opts, work_dir):
    """
    process submodules for an extracted repository

    After extracting a repository to a working tree, this call can be used to
    extract any tracked submodules configured on the repository. The
    ``.gitmodules`` file is parsed for submodules and caches will be populated
    for each submodule. This call is recursive.

    Args:
        opts: the extraction options
        work_dir: the working directory to look for submodules

    Returns:
        ``True`` if submodules have been processed; ``False`` otherwise
    """

    git_modules_file = os.path.join(work_dir, '.gitmodules')
    if not os.path.exists(git_modules_file):
        return True

    debug('parsing git submodules file: {}', git_modules_file)
    cfg = GIT.parse_cfg_file(git_modules_file)
    if not cfg:
        err('failed to parse git submodule')
        return False

    for sec_name in cfg.sections():
        if not sec_name.startswith('submodule'):
            continue

        if not cfg.has_option(sec_name, 'path') or \
                not cfg.has_option(sec_name, 'url'):
            debug('submodule section missing path/url')
            continue

        submodule_path = cfg.get(sec_name, 'path')
        submodule_revision = None
        if cfg.has_option(sec_name, 'branch'):
            submodule_revision = cfg.get(sec_name, 'branch')
        submodule_url = cfg.get(sec_name, 'url')
        log('extracting submodule ({}): {}', opts.name, submodule_path)
        debug('submodule revision: {}',
            submodule_revision if submodule_revision else '(none)')

        ckey = pkg_cache_key(submodule_url)
        root_cache_dir = os.path.abspath(
            os.path.join(opts.cache_dir, os.pardir))
        sm_cache_dir = os.path.join(root_cache_dir, ckey)

        postfix_path = os.path.split(submodule_path)
        sm_work_dir = os.path.join(work_dir, *postfix_path)

        if not _workdir_extract(sm_cache_dir, sm_work_dir, submodule_revision):
            return False

        # process nested submodules
        if not _process_submodules(opts, sm_work_dir):
            return False

    return True


def _workdir_extract(cache_dir, work_dir, revision):
    """
    extract a provided revision from a cache (bare) repository to a work tree

    Using a provided bare repository (``cache_dir``) and a working tree
    (``work_dir``), extract the contents of the repository using the providing
    ``revision`` value. This call will force the working directory to match the
    target revision. In the case where the work tree is diverged, the contents
    will be replaced with the origin's revision.

    Args:
        cache_dir: the cache repository
        work_dir: the working directory
        revision: the revision

    Returns:
        ``True`` if the extraction has succeeded; ``False`` otherwise
    """

    git_dir = '--git-dir=' + cache_dir
    work_tree = '--work-tree=' + work_dir

    # if a revision is not provided, extract the HEAD from the cache
    if not revision:
        revision = GIT.extract_submodule_revision(cache_dir)
        if not revision:
            return False

    log('checking out target revision into work tree')
    if not GIT.execute([git_dir, work_tree, '-c', 'advice.detachedHead=false',
                'checkout', '--force', revision],
            cwd=work_dir):
        err('unable to checkout revision')
        return False

    log('ensure target revision is up-to-date in work tree')
    origin_revision = 'origin/{}'.format(revision)
    output = []
    if GIT.execute([git_dir, 'rev-parse', '--quiet', '--verify',
            origin_revision], quiet=True, capture=output):
        remote_revision = ''.join(output)

        output = []
        GIT.execute([git_dir, 'rev-parse', '--quiet', '--verify', 'HEAD'],
            quiet=True, capture=output)
        local_revision = ''.join(output)

        debug('remote revision: {}', remote_revision)
        debug('local revision: {}', local_revision)

        if local_revision != remote_revision:
            warn('diverged revision detected; attempting to correct...')
            if not GIT.execute(
                    [
                        git_dir,
                        work_tree,
                        'reset',
                        '--hard',
                        origin_revision,
                    ], cwd=work_dir):
                err('unable to checkout revision')
                return False

    return True
