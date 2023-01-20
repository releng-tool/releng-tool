# -*- coding: utf-8 -*-
# Copyright 2018-2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.tool.cvs import CVS
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.io import interpret_stem_extension
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
import os
import sys
import tarfile


def fetch(opts):
    """
    support fetching from cvs sources

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

    cache_basename = os.path.basename(cache_file)
    cache_stem, __ = interpret_stem_extension(cache_basename)

    if not CVS.exists():
        err('unable to fetch package; cvs is not installed')
        return None

    note('fetching {}...', name)
    sys.stdout.flush()

    try:
        cvsroot, module = site.rsplit(' ', 1)
    except ValueError:
        err('''\
improper cvs site defined

The provided CVS site does not define both the CVSROOT as well as the target
module to checkout. For example:

    :pserver:anonymous@cvs.example.com:/var/lib/cvsroot mymodule

 Site: {}''', site)
        return None

    log('checking out sources')
    if not CVS.execute(['-d', cvsroot, 'checkout', '-d', cache_stem,
            '-r', revision, module], cwd=work_dir):
        err('unable to checkout module')
        return None

    cvs_module_dir = os.path.join(work_dir, cache_stem)
    if not os.path.exists(cvs_module_dir):
        err('no sources available for the provided revision')
        return None

    log('caching sources')

    cache_dir = os.path.abspath(os.path.join(cache_file, os.pardir))
    if not ensure_dir_exists(cache_dir):
        return None

    def cvs_filter(info):
        if info.name.endswith('CVS'):
            return None
        return info

    with tarfile.open(cache_file, 'w:gz') as tar:
        tar.add(cvs_module_dir, arcname=cache_stem, filter=cvs_filter)

    return cache_file
