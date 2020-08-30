#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2020 releng-tool

from ..tool.git import *
from ..util.io import ensureDirectoryExists
from ..util.io import pathRemove
from ..util.log import *
import os
import sys

def fetch(opts):
    """
    support fetching from git sources

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        ``True`` if the fetch stage is completed; ``False`` otherwise
    """

    assert opts
    cache_dir = opts.cache_dir
    name = opts.name
    revision = opts.revision
    site = opts.site

    if not GIT.exists():
        err('unable to fetch package; git is not installed')
        return None

    git_dir = '--git-dir=' + cache_dir

    # check if we have the target revision; if so, full stop
    if os.path.isdir(cache_dir) and not opts.ignore_cache:
        if revision_exists(git_dir, revision):
            return cache_dir

    note('fetching {}...'.format(name))
    sys.stdout.flush()

    # if we have a cache dir, ensure it's stable
    #
    # If we have a cache directory for this page but didn't find the the target
    # revision above, first check if the Git cache has been corrupted. If
    # anything is suspected wrong, start from a fresh state.
    has_cache = False
    if os.path.isdir(cache_dir):
        if opts.ignore_cache:
            has_cache = True
        else:
            log('cache directory exists for package; validating')
            if GIT.execute([git_dir, 'fsck', '--full'], cwd=cache_dir,
                    quiet=True):
                has_cache = True
            else:
                log('cache directory has errors; will re-downloaded')

                if not pathRemove(cache_dir):
                    err('''unable to cleanup cache folder for package
 (cache folder: {})'''.format(cache_dir))
                    return None

    # if we have no cache for this repository, build one
    if not has_cache:
        if not ensureDirectoryExists(cache_dir):
            return None

        if not GIT.execute([git_dir, 'init', '--bare'], cwd=cache_dir):
            err('unable to initialize bare git repository')
            return None

    # ensure origin is properly configured
    #
    # Silently try to add origin first, to lazily handle a missing case
    # followed by an explicit configuration check on forcing the origin value.
    GIT.execute([git_dir, 'remote', 'add', 'origin', site],
        cwd=cache_dir, quiet=True)
    if not GIT.execute([git_dir, 'remote', 'set-url', 'origin', site],
            cwd=cache_dir):
        err('unable to ensure origin is set on repository cache')
        return None

    log('fetching most recent sources')
    if not GIT.execute([git_dir, 'fetch', '--progress', 'origin',
            '+refs/heads/*:refs/remotes/origin/*',
            '+refs/tags/*:refs/tags/*'], cwd=cache_dir):
        err('unable to fetch branches/tags from remote repository')
        return None

    log('verifying target revision exists')
    if not revision_exists(git_dir, revision):
        err('unable to find matching revision in repository: ' + name)
        err(' (revision: {}) '.format(revision))
        return None

    return cache_dir

def revision_exists(git_dir, revision):
    """
    check if the provided revision exists

    With attempt to find if the provided revision values (be it a branch, tag or
    hash value) exists in the provided Git directory.

    Args:
        git_dir: the Git directory
        revision: the revision (branch, tag, hash) to look for

    Returns:
        ``True`` if the revision exists; ``False`` otherwise
    """

    output = []
    if not GIT.execute([git_dir, 'rev-parse', '--quiet', '--verify',
            revision], quiet=True, capture=output):
        if not GIT.execute([git_dir, 'rev-parse', '--quiet', '--verify',
                'origin/' + revision], quiet=True, capture=output):
            return False

    # confirm a hash-provided revision exists
    #
    # A call to `rev-parse` with a full hash may succeed even through the
    # hash does not exist in a repository (short hashes are valid though).
    # To handle this case, check if the revision matches the returned hash
    # valid provided. If so, perform a `cat-file` request to ensure the long
    # hash entry is indeed a valid commit.
    if output and output[0] == revision:
        if not GIT.execute([git_dir, 'cat-file', '-t', revision], quiet=True):
            return False

    return True
