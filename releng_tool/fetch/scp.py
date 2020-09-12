#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ..tool.scp import *
from ..util.log import *
import sys

def fetch(opts):
    """
    support fetching from scp sources

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
    site = opts.site
    work_dir = opts.work_dir

    if not SCP.exists():
        err('unable to fetch package; scp is not installed')
        return None

    note('fetching {}...'.format(name))
    sys.stdout.flush()

    if not SCP.execute(['-o', 'BatchMode yes', site, cache_file], cwd=work_dir):
        err('unable to secure-copied file from target')
        return None
    log('successfully secure-copied file from target')

    return cache_file
