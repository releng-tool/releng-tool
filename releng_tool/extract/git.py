# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages import pkg_cache_key
from releng_tool.tool.git import GIT
from releng_tool.util.io_copy import path_copy_into
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import verbose
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
    if not _workdir_extract(opts, cache_dir, work_dir, revision):
        return False

    # extract submodules (if configured to do so)
    if opts._git_submodules:
        if not _process_submodules(opts, cache_dir, work_dir, revision):
            return False

    return True


def _process_submodules(opts, cache_dir, work_dir, revision):
    """
    process submodules for an extracted repository

    After extracting a repository to a working tree, this call can be used to
    extract any tracked submodules configured on the repository. The
    ``.gitmodules`` file is parsed for submodules and caches will be populated
    for each submodule. This call is recursive.

    Args:
        opts: the extraction options
        cache_dir: the cache repository that may be holding submodules
        work_dir: the working directory to look for submodules
        revision: the revision of the repository that may be holding submodules

    Returns:
        ``True`` if submodules have been processed; ``False`` otherwise
    """

    git_dir = '--git-dir=' + cache_dir

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
        debug('submodule path: {}', submodule_path)

        submodule_url = cfg.get(sec_name, 'url')
        debug('submodule url: {}', submodule_url)

        rev_ref = f'{revision}:{submodule_path}'
        rv, submodule_revision = GIT.execute_rv(git_dir, 'rev-parse', rev_ref)
        if rv != 0:
            err(f'unable to determine submodule revision: {submodule_path}')
            return False

        log('extracting submodule ({}): {}', opts.name, submodule_path)
        debug('submodule revision: {}', submodule_revision)

        ckey = pkg_cache_key(submodule_url)
        root_cache_dir = os.path.abspath(
            os.path.join(opts.cache_dir, os.pardir))
        sm_cache_dir = os.path.join(root_cache_dir, ckey)

        postfix_path = os.path.split(submodule_path)
        sm_work_dir = os.path.join(work_dir, *postfix_path)

        if not _workdir_extract(
                opts, sm_cache_dir, sm_work_dir, submodule_revision):
            return False

        # process nested submodules
        if not _process_submodules(
                opts, sm_cache_dir, sm_work_dir, submodule_revision):
            return False

    return True


def _workdir_extract(opts, cache_dir, work_dir, revision):
    """
    extract a provided revision from a cached repository to a work tree

    Using a provided cached repository (``cache_dir``) and a working tree
    (``work_dir``), extract the contents of the repository using the providing
    ``revision`` value. This call will force the working directory to match the
    target revision. In the case where the work tree is diverged, the contents
    will be replaced with the origin's revision.

    Args:
        opts: the extraction options
        cache_dir: the cache repository
        work_dir: the working directory
        revision: the revision

    Returns:
        ``True`` if the extraction has succeeded; ``False`` otherwise
    """

    git_dir = '--git-dir=' + cache_dir
    work_tree = '--work-tree=' + work_dir

    log(f'checking out revision ({revision}) into work tree')
    if not GIT.execute([git_dir, work_tree, '-c', 'advice.detachedHead=false',
                'checkout', '--force', revision],
            cwd=work_dir):
        err('unable to checkout revision')
        return False

    verbose('ensure target revision is up-to-date in work tree')
    origin_revision = f'origin/{revision}'
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
            warn(f'''\
diverged revision detected; attempting to correct...
  local: {local_revision}
 remote: {remote_revision}''')

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

    # always dump git hash to aid in logging
    output = []
    GIT.execute([git_dir, 'rev-parse', '--quiet', '--verify', 'HEAD'],
        quiet=True, capture=output)
    local_revision = ''.join(output)
    if revision != local_revision:
        log(f'working tree hash: {local_revision}')

    # Setup a `.git` file with a path to the cache directory. This should
    # help provide a way for developers to interact with Git inside a
    # package's build directory for development/testing purposes.
    #
    # Also, there is an alternative quirk which just performs a full copy
    # of the cache into the output directory. This can be useful in mixed
    # partition/permission environments, where the Git client may complain
    # about the referenced cache directory not being a safe directory.
    git_file = os.path.join(work_dir, '.git')
    if not os.path.exists(git_file):
        if 'releng.git.replicate_cache' in opts._quirks:
            debug('attempting to replicate .git directory')
            if not path_copy_into(cache_dir, git_file, critical=False):
                verbose('failed to replicate .git directory')
        else:
            with open(git_file, 'w') as f:
                f.write(f'gitdir: {cache_dir}\n')

    return True
