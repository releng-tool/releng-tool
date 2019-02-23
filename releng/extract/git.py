#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ..tool.git import *
from ..util.log import *

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
    if not GIT.execute([git_dir, work_tree, 'pull', 'origin', revision],
            cwd=work_dir):
        err('unable to checkout revision')
        return False

    return True
