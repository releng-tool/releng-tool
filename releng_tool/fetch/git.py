# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.packages import pkg_cache_key
from releng_tool.tool.git import GIT
from releng_tool.util.enum import Enum
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.io import path_remove
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.log import warn
from releng_tool.util.log import verbose
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

    # check if we have the target revision cached; if so, package is ready
    if os.path.isdir(cache_dir) and not opts.ignore_cache:
        if revision_exists(git_dir, revision) == GitExistsType.EXISTS:
            # ensure configuration is properly synchronized
            if not _sync_git_configuration(opts):
                return None

            # return cache dir if not verifying or verification succeeds
            if not opts._git_verify_revision or _verify_revision(
                    git_dir, revision, quiet=True):
                return cache_dir

    note('fetching {}...'.format(name))
    sys.stdout.flush()

    # if we have a cache dir, ensure it's stable
    #
    # If we have a cache directory for this page but didn't find the the target
    # revision above, first check if the Git cache has been corrupted. If
    # anything is suspected wrong, start from a fresh state.
    has_cache = False
    clean_cache = False
    if os.path.isdir(cache_dir):
        if opts.ignore_cache:
            verbose('sanity checking if cached directory is valid')
            if GIT.execute([git_dir, 'rev-parse'], cwd=cache_dir, quiet=True):
                has_cache = True
            else:
                clean_cache = True
        else:
            log('cache directory exists for package; validating')
            if GIT.execute([git_dir, 'fsck', '--full'], cwd=cache_dir,
                    quiet=True):
                has_cache = True
            else:
                clean_cache = True

    if clean_cache:
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
    if not _sync_git_configuration(opts):
        return None

    # fetch sources for this repository
    if not _fetch_srcs(opts, cache_dir, revision, refspecs=opts._git_refspecs):
        return None

    # verify revision (if configured to check it)
    if opts._git_verify_revision:
        if not _verify_revision(git_dir, revision):
            err("""\
failed to validate git revision

Package has been configured to require the verification of the GPG signature
for the target revision. The verification has failed. Ensure that the revision
is signed and that the package's public key has been registered in the system.

      Package: {}
     Revision: {}""".format(name, revision))
            return None

    # fetch submodules (if configured to do so)
    if opts._git_submodules:
        if not _fetch_submodules(opts, cache_dir, revision):
            return None

    return cache_dir

def _fetch_srcs(opts, cache_dir, revision, desc=None, refspecs=None):
    """
    invokes a git fetch call of the configured origin into a bare repository

    With a provided cache directory (``cache_dir``; bare repository), fetch the
    contents of a configured origin into the directory. The fetch call will
    use a restricted depth, unless configured otherwise. In the event a target
    revision cannot be found (if provided), an unshallow fetch will be made.

    This call may be invoked without a revision provided -- specifically, this
    can occur for submodule configurations which do not have a specific revision
    explicitly set.

    Args:
        opts: fetch options
        cache_dir: the bare repository to fetch into
        revision: expected revision desired from the repository
        desc (optional): description to use for error message
        refspecs (optional): additional refspecs to add to the fetch call

    Returns:
        ``True`` if the fetch was successful; ``False`` otherwise
    """

    git_dir = '--git-dir=' + cache_dir

    if not desc:
        desc = 'repository: {}'.format(opts.name)

    log('fetching most recent sources')
    prepared_fetch_cmd = [
        git_dir,
        'fetch',
        '--progress',
        '--prune',
        'origin',
    ]

    # limit fetch depth
    target_depth = 1
    if opts._git_depth is not None:
        target_depth = opts._git_depth
    limited_fetch = (target_depth and 'releng.git.no_depth' not in opts._quirks)

    depth_cmds = [
        '--depth',
        str(target_depth),
    ]

    # if a revision is provided, first attempt to do a revision-specific fetch
    quick_fetch = 'releng.git.no_quick_fetch' not in opts._quirks
    if revision and quick_fetch:
        ls_cmd = [
            'ls-remote',
            'origin',
        ]
        debug('checking if tag exists on remote')
        if GIT.execute(ls_cmd + ['--tags', revision],
                cwd=cache_dir, quiet=True):
            debug('attempting a tag reference fetch operation')
            fetch_cmd = list(prepared_fetch_cmd)
            fetch_cmd.append('+refs/tags/{0}:refs/tags/{0}'.format(revision))
            if limited_fetch:
                fetch_cmd.extend(depth_cmds)

            if GIT.execute(fetch_cmd, cwd=cache_dir):
                debug('found the reference')
                return True

        debug('checking if reference exists on remote')
        if GIT.execute(ls_cmd + ['--heads', revision],
                cwd=cache_dir, quiet=True):
            debug('attempting a head reference fetch operation')
            fetch_cmd = list(prepared_fetch_cmd)
            fetch_cmd.append(
                '+refs/heads/{0}:refs/remotes/origin/{0}'.format(revision))
            if limited_fetch:
                fetch_cmd.extend(depth_cmds)

            if GIT.execute(fetch_cmd, cwd=cache_dir):
                debug('found the reference')
                return True

    # fetch standard (and configured) refspecs
    std_refspecs = [
        '+refs/heads/*:refs/remotes/origin/*',
        '+refs/tags/*:refs/tags/*',
    ]
    prepared_fetch_cmd.extend(std_refspecs)

    # allow fetching addition references if configured (e.g. pull requests)
    if refspecs:
        for ref in refspecs:
            prepared_fetch_cmd.append(
                '+refs/{0}:refs/remotes/origin/{0}'.format(ref))

    fetch_cmd = list(prepared_fetch_cmd)
    if limited_fetch:
        fetch_cmd.extend(depth_cmds)

    if not GIT.execute(fetch_cmd, cwd=cache_dir):
        err('unable to fetch branches/tags from remote repository')
        return False

    if revision:
        verbose('verifying target revision exists')
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
                return False

            if revision_exists(git_dir, revision) != GitExistsType.EXISTS:
                err('unable to find matching revision in ' + desc)
                err(' (revision: {}) '.format(revision))
                return False
        else:
            err('unable to find matching revision in ' + desc)
            err(' (revision: {}) '.format(revision))
            return False

    return True

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

def _sync_git_configuration(opts):
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
        opts: fetch options

    Returns:
        ``True`` if the configuration has been synchronized; ``False`` otherwise
    """

    cache_dir = opts.cache_dir
    git_dir = '--git-dir=' + cache_dir
    site = opts.site

    if not _sync_git_origin(cache_dir, site):
        return False

    # apply repository-specific configurations
    if opts._git_config:
        for key, val in opts._git_config.items():
            if not GIT.execute([git_dir, 'config', key, val], cwd=cache_dir):
                err('unable to apply configuration entry "{}" with value "{}"',
                    key, val)
                return False

    return True

def _sync_git_origin(cache_dir, site):
    """
    synchronize an origin site to a git configuration

    Ensures the configured site is set as the origin of the repository. This is
    to help handle scenarios where a package's site has changed while content is
    already cached.

    Args:
        cache_dir: the cache/bare repository
        site: the site that should be set

    Returns:
        ``True`` if the site is synchronized; ``False`` otherwise
    """

    git_dir = '--git-dir=' + cache_dir

    # silently try to add origin first, to lazily handle a missing case
    GIT.execute([git_dir, 'remote', 'add', 'origin', site],
        cwd=cache_dir, quiet=True)

    if not GIT.execute([git_dir, 'remote', 'set-url', 'origin', site],
            cwd=cache_dir):
        err('unable to ensure origin is set on repository cache')
        return False

    return True

def _fetch_submodules(opts, cache_dir, revision):
    """
    fetch the submodules on a provided cache/bar repository

    Using a provided bare repository, submodules configured at the provided
    revision will be fetched into the bare repository's modules directory. If it
    has been detected that a submodule contains additional submodules, they will
    also be fetched into a cache directory.

    Args:
        opts: fetch options
        cache_dir: the cache/bare repository
        revision: the revision (branch, tag, hash) to fetch

    Returns:
        ``True`` if submodules have been processed; ``False`` otherwise
    """
    assert revision

    git_dir = '--git-dir=' + cache_dir

    # find a .gitmodules configuration on the target revision
    submodule_ref = '{}:.gitmodules'.format(revision)
    rv, raw_submodules = GIT.execute_rv(git_dir, 'show', submodule_ref)
    if rv != 0:
        submodule_ref = 'origin/' + submodule_ref
        rv, raw_submodules = GIT.execute_rv(git_dir, 'show', submodule_ref)
        if rv != 0:
            verbose('no git submodules file detected for this revision')
            return True

    debug('parsing git submodules file...')
    cfg = GIT.parse_cfg_str(raw_submodules)
    if not cfg:
        verbose('no git submodules file detected for this revision')
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
        verbose('detected submodule: {}', submodule_path)
        debug('submodule revision: {}',
            submodule_revision if submodule_revision else '(none)')
        debug('submodule url: {}', submodule_url)

        ckey = pkg_cache_key(submodule_url)
        root_cache_dir = os.path.abspath(
            os.path.join(opts.cache_dir, os.pardir))
        submodule_cache_dir = os.path.join(root_cache_dir, ckey)
        verbose('submodule_cache_dir: {}', submodule_cache_dir)

        # check to make sure the submodule's path isn't pointing to a relative
        # path outside the expected cache base
        check_abs = os.path.abspath(submodule_cache_dir)
        check_common = os.path.commonprefix((submodule_cache_dir, check_abs))
        if check_abs != check_common:
            err('unable to process submodule pathed outside of bare repository')
            verbose('submodule expected base: {}', check_common)
            verbose('submodule absolute path: {}', check_abs)
            return False

        # fetch/cache the submodule repository
        if not _fetch_submodule(opts, submodule_path, submodule_cache_dir,
                submodule_revision, submodule_url):
            return False

        # if a revision is not provided, extract the HEAD from the cache
        if not submodule_revision:
            submodule_revision = GIT.extract_submodule_revision(
                submodule_cache_dir)
            if not submodule_revision:
                return False

        # process nested submodules
        if not _fetch_submodules(opts, submodule_cache_dir, submodule_revision):
            return False

    return True

def _fetch_submodule(opts, name, cache_dir, revision, site):
    """
    fetch a submodule into a provided cache/bar repository

    Fetches an individual submodule into the provided cache directory. The
    origin of the submodule is provided via the ``site`` argument. A revision,
    if provided, can be used to help verify the target revision desired for a
    submodule; however, it is not required (e.g. when a repository does not set
    an explicit submodule revision).

    Args:
        opts: fetch options
        name: the name of the submodule (for state messages)
        cache_dir: the cache/bare repository to fetch into
        revision: the revision (branch, tag, hash) to fetch
        site: the site to fetch the submodule from

    Returns:
        ``True`` if the submodule has been fetched; ``False`` otherwise
    """
    git_dir = '--git-dir=' + cache_dir

    # check if we have the target revision cached; if so, submodule is ready
    if os.path.isdir(cache_dir) and not opts.ignore_cache:
        if not revision:
            return _sync_git_origin(cache_dir, site)

        if revision_exists(git_dir, revision) == GitExistsType.EXISTS:
            return _sync_git_origin(cache_dir, site)

    log('processing submodule (package: {}) {}...'.format(opts.name, name))
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
            log('cache directory exists for submodule; validating')
            if GIT.execute([git_dir, 'fsck', '--full'], cwd=cache_dir,
                    quiet=True):
                has_cache = True
            else:
                log('cache directory has errors; will re-downloaded')

                if not path_remove(cache_dir):
                    err('''unable to cleanup cache folder for package
 (cache folder: {})'''.format(cache_dir))
                    return False

    # if we have no cache for this repository, build one
    if not has_cache:
        if not ensure_dir_exists(cache_dir):
            return False

        if not GIT.execute([git_dir, 'init', '--bare'], cwd=cache_dir):
            err('unable to initialize bare git repository')
            return False

    # ensure configuration is properly synchronized
    if not _sync_git_origin(cache_dir, site):
        return False

    # fetch sources for this submodule
    desc = 'submodule ({}): {}'.format(opts.name, name)
    return _fetch_srcs(opts, cache_dir, revision, desc=desc)

def _verify_revision(git_dir, revision, quiet=False):
    """
    verify the gpg signature for a target revision

    The GPG signature for a provided revision (tag or commit) will be checked
    to validate the revision.

    Args:
        git_dir: the Git directory
        revision: the revision to verify
        quiet (optional): whether or not the log if verification is happening

    Returns:
        ``True`` if the revision is signed; ``False`` otherwise
    """

    if not quiet:
        log('verifying the gpg signature on the target revision')
    else:
        verbose('verifying the gpg signature on the target revision')

    if GIT.execute([git_dir, 'rev-parse', '--quiet',
            '--verify', revision + '^{tag}'], quiet=True):
        verified_cmd = 'verify-tag'
    else:
        verified_cmd = 'verify-commit'

        # acquire the commit if (if not already set), to ensure we can verify
        # against commits or branches
        rv, revision = GIT.execute_rv(git_dir, 'rev-parse', revision)
        if rv != 0:
            verbose('failed to determine the commit id for a revision')
            return False

    return GIT.execute([git_dir, verified_cmd, revision], quiet=quiet)
