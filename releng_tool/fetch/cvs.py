# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool.

from ..tool.cvs import *
from ..util.io import ensureDirectoryExists
from ..util.io import interpretStemExtension
from ..util.log import *
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
    cache_stem, __ = interpretStemExtension(cache_basename)

    if not CVS.exists():
        err('unable to fetch package; cvs is not installed')
        return None

    note('fetching {}...'.format(name))
    sys.stdout.flush()

    try:
        cvsroot, module = site.rsplit(' ', 1)
    except ValueError:
        err('improper cvs site defined')
        err("""\
The provided CVS site does not define both the CVSROOT as well as the target
module to checkout. For example:

    :pserver:anonymous@cvs.example.com:/var/lib/cvsroot mymodule

 Site: {}""".format(site))
        return None

    log('checking out sources')
    if not CVS.execute(['-d', cvsroot, 'checkout', '-d', cache_stem,
            '-r', revision, module], cwd=work_dir):
        err('unable to checkout module')
        return None

    log('caching sources')
    def cvs_filter(info):
        if info.name.endswith('CVS'):
            return None
        return info

    cache_dir = os.path.abspath(os.path.join(cache_file, os.pardir))
    if not ensureDirectoryExists(cache_dir):
        return None

    cvs_module_dir = os.path.join(work_dir, cache_stem)
    with tarfile.open(cache_file, 'w:gz') as tar:
        tar.add(cvs_module_dir, arcname=cache_stem, filter=cvs_filter)

    return cache_file
