# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.tool.svn import SVN
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
import os
import sys
import tarfile


def fetch(opts):
    """
    support fetching from svn sources

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        ``True`` if the fetch stage is completed; ``False`` otherwise
    """

    assert opts
    cache_file = opts.cache_file
    name = opts.name
    revision = opts.revision
    site = opts.site
    work_dir = opts.work_dir

    if not SVN.exists():
        err('unable to fetch package; svn is not installed')
        return None

    note('fetching {}...'.format(name))
    sys.stdout.flush()

    log('checking out sources')
    if not SVN.execute(['checkout', '-r', revision, site, work_dir],
            cwd=work_dir):
        err('unable to checkout module')
        return None

    log('caching sources')
    def svn_exclude(file):
        if file.endswith('.svn'):
            return True
        return False

    # ensure cache file's directory exists
    cache_dir = os.path.abspath(os.path.join(cache_file, os.pardir))
    if not ensure_dir_exists(cache_dir):
        return None

    with tarfile.open(cache_file, 'w:gz') as tar:
        tar.add(work_dir, arcname=name, exclude=svn_exclude)

    return cache_file
