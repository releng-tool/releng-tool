# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.tool.git import GIT
from releng_tool.util.enum import Enum
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.io import path_remove
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.log import warn
import os
import sys

class GitExistsType(Enum):
    """
    git exists type

    Enumeration of types of existence states when verifying a configured
    revision exists in a Git repository.

    Attributes:
        EXISTS: revision exists
        MISSING: revision does not exist
        MISSING_HASH: a hash-provided revision does not exist
    """
    EXISTS = 'exists'
    MISSING = 'missing'
    MISSING_HASH = 'missing_hash'

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

    if not GIT.exists():
        err('unable to fetch package; git is not installed')
        return None

    git_dir = '--git-dir=' + cache_dir

    # check if we have the target revision; if so, full stop
    if os.path.isdir(cache_dir) and not opts.ignore_cache:
        if revision_exists(git_dir, revision) == GitExistsType.EXISTS:
            # ensure configuration is properly synchronized
            if not sync_git_configuration(git_dir, opts):
                return None

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

                if not path_remove(cache_dir):
                    err('''unable to cleanup cache folder for package
 (cache folder: {})'''.format(cache_dir))
                    return None

    # if we have no cache for this repository, build one
    if not has_cache:
        if not ensure_dir_exists(cache_dir):
            return None

        if not GIT.execute([git_dir, 'init', '--bare'], cwd=cache_dir):
            err('unable to initialize bare git repository')
            return None

    # ensure configuration is properly synchronized
    if not sync_git_configuration(git_dir, opts):
        return None

    log('fetching most recent sources')
    prepared_fetch_cmd = [
        git_dir,
        'fetch',
        '--progress',
        'origin',
        '+refs/heads/*:refs/remotes/origin/*',
        '+refs/tags/*:refs/tags/*',
    ]

    # allow fetching addition references if configured (e.g. pull requests)
    if opts._git_refspecs:
        for ref in opts._git_refspecs:
            prepared_fetch_cmd.append(
                '+refs/{}:refs/remotes/origin/{}'.format(ref, ref))

    # limit fetch depth
    target_depth = 1
    if opts._git_depth is not None:
        target_depth = opts._git_depth
    limited_fetch = (target_depth and 'releng.git.no_depth' not in opts._quirks)

    fetch_cmd = list(prepared_fetch_cmd)
    if limited_fetch:
        fetch_cmd.append('--depth')
        fetch_cmd.append(str(target_depth))

    if not GIT.execute(fetch_cmd, cwd=cache_dir):
        err('unable to fetch branches/tags from remote repository')
        return None

    log('verifying target revision exists')
    exists_state = revision_exists(git_dir, revision)
    if exists_state == GitExistsType.EXISTS:
        pass
    elif (exists_state == GitExistsType.MISSING_HASH and
            limited_fetch and opts._git_depth is None):
        warn('failed to find hash on depth-limited fetch; fetching all...')

        fetch_cmd = list(prepared_fetch_cmd)
        fetch_cmd.append('--unshallow')

        if not GIT.execute(fetch_cmd, cwd=cache_dir):
            err('unable to unshallow fetch state')
            return None

        if revision_exists(git_dir, revision) != GitExistsType.EXISTS:
            err('unable to find matching revision in repository: ' + name)
            err(' (revision: {}) '.format(revision))
            return None
    else:
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
        a value of ``GitExistsType``
    """

    output = []
    if not GIT.execute([git_dir, 'rev-parse', '--quiet', '--verify',
            revision], quiet=True, capture=output):
        if not GIT.execute([git_dir, 'rev-parse', '--quiet', '--verify',
                'origin/' + revision], quiet=True, capture=output):
            return GitExistsType.MISSING

    # confirm a hash-provided revision exists
    #
    # A call to `rev-parse` with a full hash may succeed even through the
    # hash does not exist in a repository (short hashes are valid though).
    # To handle this case, check if the revision matches the returned hash
    # valid provided. If so, perform a `cat-file` request to ensure the long
    # hash entry is indeed a valid commit.
    if output and output[0] == revision:
        if not GIT.execute([git_dir, 'cat-file', '-t', revision], quiet=True):
            return GitExistsType.MISSING_HASH

    return GitExistsType.EXISTS

def sync_git_configuration(git_dir, opts):
    """
    ensure the git configuration is properly synchronized with this repository

    This call ensures that various Git configuration options are properly
    synchronized with the cached Git repository. This includes:

    - Ensuring the configured site is set as the origin of the repository. This
       is to help handle scenarios where a package's site has changed while
       content is already cached.
    - Ensure various `git config` options are set, if specific repository
       options need to be set (e.g. overriding `core.autocrlf`).

    Args:
        git_dir: the Git directory
        opts: fetch options

    Returns:
        ``True`` if the configuration has been synchronized; ``False`` otherwise
    """

    cache_dir = opts.cache_dir
    site = opts.site

    # silently try to add origin first, to lazily handle a missing case
    GIT.execute([git_dir, 'remote', 'add', 'origin', site],
        cwd=cache_dir, quiet=True)

    if not GIT.execute([git_dir, 'remote', 'set-url', 'origin', site],
            cwd=cache_dir):
        err('unable to ensure origin is set on repository cache')
        return False

    # apply repository-specific configurations
    if opts._git_config:
        for key, val in opts._git_config.items():
            if not GIT.execute([git_dir, 'config', key, val], cwd=cache_dir):
                err('unable to apply configuration entry "{}" with value "{}"',
                    key, val)
                return False

    return True
