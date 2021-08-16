# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.tool.git import GIT
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import warn

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

    git_dir = '--git-dir=' + cache_dir
    work_tree = '--work-tree=' + work_dir

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
                        origin_revision,
                    ], cwd=work_dir):
                err('unable to checkout revision')
                return False

    return True
