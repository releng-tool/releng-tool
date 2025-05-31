# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages import pkg_cache_key
from releng_tool.tool.git import GIT
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_remove import path_remove
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.strccenum import StrCcEnum
import os


class GitExistsType(StrCcEnum):
    """
    git exists type

    Enumeration of types of existence states when verifying a configured
    revision exists in a Git repository.

    Attributes:
        EXISTS_BRANCH: branch exists
        EXISTS_HASH: hash exists
        EXISTS_TAG: tag exists
        MISSING: revision does not exist
        MISSING_HASH: a hash-provided revision does not exist
    """
    EXISTS_BRANCH = 'exists_branch'
    EXISTS_HASH = 'exists_hash'
    EXISTS_TAG = 'exists_tag'
    MISSING = 'missing'
    MISSING_HASH = 'missing_hash'

# types indicating a revision exists
REVISION_EXISTS = [
    GitExistsType.EXISTS_BRANCH,
    GitExistsType.EXISTS_HASH,
    GitExistsType.EXISTS_TAG,
]


def fetch(opts):
    """
    support fetching from git sources

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        the fetched cache directory; ``None`` if fetching has failed
    """

    assert opts

    if not GIT.exists():
        err('unable to fetch package; git is not installed')
        return None

    if opts._local_srcs:
        return fetch_local_srcs(opts)

    return fetch_default(opts)


def fetch_default(opts):
    """
    support fetching from git sources in a default operating mode

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        the fetched cache directory; ``None`` if fetching has failed
    """

    cache_dir = opts.cache_dir
    name = opts.name
    revision = opts.revision

    git_dir = '--git-dir=' + cache_dir

    # check if we have the target revision cached; if so, package is ready
    if os.path.isdir(cache_dir) and not opts.ignore_cache:
        erv = revision_exists(git_dir, revision)
        if erv in REVISION_EXISTS:
            # ensure configuration is properly synchronized
            if not _sync_git_configuration(opts):
                return None

            # if no explicit ignore-cache request and if the revision is a
            # branch, force ignore-cache on and allow fetching to proceed
            if opts.ignore_cache is None and erv == GitExistsType.EXISTS_BRANCH:
                opts.ignore_cache = True
            # return cache dir if not verifying or verification succeeds
            elif not opts._git_verify_revision or _verify_revision(
                    git_dir, revision, quiet=True):
                return cache_dir

    note('fetching {}...', name)

    # validate any cache directory (if one exists)
    has_cache, bad_validation = _validate_cache(cache_dir)
    if bad_validation:
        return None

    # if we have no cache for this repository, build one
    if not has_cache:
        if not mkdir(cache_dir):
            return None

        if not _create_bare_git_repo(cache_dir):
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
            err('''\
failed to validate git revision

Package has been configured to require the verification of the GPG signature
for the target revision. The verification has failed. Ensure that the revision
is signed and that the package's public key has been registered in the system.

      Package: {}
     Revision: {}''', name, revision)
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
        desc = f'repository: {opts.name}'

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
            '--exit-code',
            'origin',
        ]
        debug('checking if tag exists on remote')
        if GIT.execute([*ls_cmd, '--tags', f'refs/tags/{revision}'],
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
        if GIT.execute([*ls_cmd, '--heads', f'refs/heads/{revision}'],
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
        if exists_state in REVISION_EXISTS:
            pass
        elif (exists_state == GitExistsType.MISSING_HASH and
                limited_fetch and opts._git_depth is None):
            warn('failed to find hash on depth-limited fetch; fetching all...')

            fetch_cmd = list(prepared_fetch_cmd)
            fetch_cmd.append('--unshallow')

            if not GIT.execute(fetch_cmd, cwd=cache_dir):
                err('unable to unshallow fetch state')
                return False

            if revision_exists(git_dir, revision) not in REVISION_EXISTS:
                err('unable to find matching revision in {}\n'
                    ' (revision: {})', desc, revision)
                return False
        else:
            err('unable to find matching revision in {}\n'
                ' (revision: {})', desc, revision)
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

    if GIT.execute([git_dir, 'rev-parse', '--quiet', '--verify',
            'refs/tags/' + revision], quiet=True):
        return GitExistsType.EXISTS_TAG

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
        if GIT.execute([git_dir, 'cat-file', '-t', revision], quiet=True):
            return GitExistsType.EXISTS_HASH

        return GitExistsType.MISSING_HASH

    return GitExistsType.EXISTS_BRANCH


def _create_bare_git_repo(cache_dir):
    """
    create a bare git repository

    This call will build a bare Git repository in the provided cache
    directory. If the repository could not be created, an error message
    will be generated and this method will return ``False``.

    Args:
        cache_dir: the cache/bare repository

    Returns:
        ``True`` if the repository could be created; ``False`` otherwise
    """

    git_dir = '--git-dir=' + cache_dir

    if GIT.execute([git_dir, 'init', '--bare', '--quiet'], cwd=cache_dir):
        # After preparing the bare repository, remove the bare flag from the
        # configuration. This is to later allow interaction with this cache
        # for developers who may wish to interact with a Git file system
        # inside the build directory. During the extraction stage, we setup
        # a `.git` file with a reference to the cache directory. This should
        # allow users to invoke Git operations from inside the build
        # directory, but the Git client can complain that it is not a valid
        # repository setup. The error goes away when the configured Git
        # directory is not bare.
        if not GIT.execute([git_dir, 'config', '--unset', 'core.bare'],
                cwd=cache_dir):
            verbose('unable to remove bare configuration on repository')

        # Disable automatic garbage collection tasks on Git repositories
        # managed in the releng-tool playground -- repositories are interim;
        # no need for extra work.
        if not GIT.execute([git_dir, 'config', 'gc.auto', '0'],
                cwd=cache_dir):
            verbose('unable to disable maintenance mode on repository')

        # Disable automatic maintenance tasks on Git repositories managed in
        # the releng-tool playground -- repositories are interim; no need for
        # extra work.
        if not GIT.execute([git_dir, 'config', 'maintenance.auto', 'false'],
                cwd=cache_dir):
            verbose('unable to disable maintenance mode on repository')

        return True

    err('unable to initialize bare git repository')
    return False


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
    tree_ref = revision
    submodule_ref = f'{tree_ref}:.gitmodules'
    rv, raw_submodules = GIT.execute_rv(git_dir, 'show', submodule_ref)
    if rv != 0:
        tree_ref = f'origin/{revision}'
        submodule_ref = f'{tree_ref}:.gitmodules'
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
        verbose('detected submodule: {}', submodule_path)

        submodule_url = cfg.get(sec_name, 'url')
        debug('submodule url: {}', submodule_url)

        rev_ref = f'{tree_ref}:{submodule_path}'
        rv, submodule_revision = GIT.execute_rv(git_dir, 'rev-parse', rev_ref)
        if rv != 0:
            err(f'unable to determine submodule revision: {submodule_path}')
            return False

        debug('submodule revision: {}', submodule_revision)

        ckey = pkg_cache_key(submodule_url)
        root_cache_dir = os.path.abspath(
            os.path.join(opts.cache_dir, os.pardir))
        submodule_cache_dir = os.path.join(root_cache_dir, ckey)

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

        if revision_exists(git_dir, revision) in REVISION_EXISTS:
            return _sync_git_origin(cache_dir, site)

    log('processing submodule (package: {}) {}...', opts.name, name)

    # validate any cache directory (if one exists)
    has_cache, bad_validation = _validate_cache(cache_dir)
    if bad_validation:
        return None

    # if we have no cache for this repository, build one
    if not has_cache:
        if not mkdir(cache_dir):
            return False

        if not _create_bare_git_repo(cache_dir):
            return False

    # ensure configuration is properly synchronized
    if not _sync_git_origin(cache_dir, site):
        return False

    # fetch sources for this submodule
    desc = f'submodule ({opts.name}): {name}'
    return _fetch_srcs(opts, cache_dir, revision, desc=desc)


def _validate_cache(cache_dir):
    """
    validate an existing cache directory to fetch on

    A fetch operation may occur on an existing cache directory, typically when
    a force-fetch or a configured revision has changed. This call helps
    validate the existing cache directory (from a bad state such as a corrupted
    repository). If a cache directory does exist,

    Args:
        cache_dir: the cache/bare repository to fetch into

    Returns:
        a 2-tuple (if a cache directory exists; and if validation failed)
    """

    git_dir = '--git-dir=' + cache_dir

    bad_validation = False
    has_cache = False
    if os.path.isdir(cache_dir):
        log('cache directory detected; validating')
        if GIT.execute([git_dir, 'rev-parse'], cwd=cache_dir, quiet=True):
            debug('cache directory validated')
            has_cache = True
        else:
            log('cache directory has errors; will re-downloaded')
            if not path_remove(cache_dir):
                err('unable to cleanup cache folder for package\n'
                    ' (cache folder: {})', cache_dir)
                bad_validation = True

    return has_cache, bad_validation


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


def fetch_local_srcs(opts):
    """
    support fetching from git sources in a local-sources mode

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        the fetched cache directory; ``None`` if fetching has failed
    """

    assert opts._build_dir
    assert opts._local_srcs

    cache_dir = opts.cache_dir
    name = opts.name
    site = opts.site
    target_dir = opts._build_dir

    note('fetching {}...', name)

    if not GIT.execute(['clone', site, '--progress', target_dir]):
        err('unable to clone git repository')
        return None

    return cache_dir
