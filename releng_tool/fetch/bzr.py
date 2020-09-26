# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ..tool.bzr import *
from ..util.io import ensure_dir_exists
from ..util.log import *
import os
import sys

def fetch(opts):
    """
    support fetching from bzr sources

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

    if not BZR.exists():
        err('unable to fetch package; bzr is not installed')
        return None

    note('fetching {}...'.format(name))
    sys.stdout.flush()

    cache_dir = os.path.abspath(os.path.join(cache_file, os.pardir))
    if not ensure_dir_exists(cache_dir):
        return None

    log('exporting sources')
    if not BZR.execute(['export', cache_file, site,
            '--format=tgz', '--root=' + name, '--revision=' + revision],
            poll=True):
        err('unable to export module')
        return None

    return cache_file
