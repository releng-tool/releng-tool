# -*- coding: utf-8 -*-
# Copyright 2018-2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.tool.hg import HG
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
import os
import sys


def fetch(opts):
    """
    support fetching from mercurial sources

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

    if not HG.exists():
        err('unable to fetch package; hg (mercurial) is not installed')
        return None

    hg_dir = ['--repository', cache_dir]

    # check if we have the target revision; if so, full stop
    if os.path.isdir(cache_dir) and not opts.ignore_cache:
        if HG.execute(hg_dir + ['--quiet', 'log', '--rev', revision],
                cwd=cache_dir, quiet=True):
            return cache_dir

    note('fetching {}...', name)
    sys.stdout.flush()

    # if we have no cache for this repository, build one
    if not os.path.isdir(cache_dir):
        if not ensure_dir_exists(cache_dir):
            return None

        if not HG.execute(['--noninteractive', '--verbose',
                'clone', '--noupdate', site, cache_dir],
                cwd=cache_dir):
            err('unable to clone mercurial repository')
            return None

    log('fetching most recent sources')
    if not HG.execute(hg_dir + ['--noninteractive', '--verbose', 'pull'],
            cwd=cache_dir):
        err('unable to fetch from remote repository')
        return None

    log('verifying target revision exists')
    if not HG.execute(hg_dir + ['--quiet', 'log', '--rev', revision],
            cwd=cache_dir, quiet=True):
        err('unable to find matching revision in repository: {}\n'
            ' (revision: {})', name, revision)
        return None

    return cache_dir
