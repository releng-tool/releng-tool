# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.cvs import CVS
from releng_tool.util.io import interpret_stem_extension
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.log import verbose
import os
import tarfile


def fetch(opts):
    """
    support fetching from cvs sources

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        the fetched cache file; ``None`` if fetching has failed
    """

    assert opts

    if not CVS.exists():
        err('unable to fetch package; cvs is not installed')
        return None

    if opts._local_srcs:
        return fetch_local_srcs(opts)

    return fetch_default(opts)


def fetch_default(opts):
    """
    support fetching from cvs sources in a default operating mode

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        the fetched cache file; ``None`` if fetching has failed
    """

    cache_file = opts.cache_file
    name = opts.name
    revision = opts.revision
    site = opts.site
    work_dir = opts.work_dir

    cache_basename = os.path.basename(cache_file)
    cache_stem, __ = interpret_stem_extension(cache_basename)

    note('fetching {}...', name)

    cvsroot, module = _extract_site(site)
    if not cvsroot or not module:
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
    if not mkdir(cache_dir):
        return None

    def cvs_filter(info):
        if info.name.endswith('CVS'):
            return None
        return info

    with tarfile.open(cache_file, 'w:gz') as tar:
        tar.add(cvs_module_dir, arcname=cache_stem, filter=cvs_filter)

    return cache_file


def fetch_local_srcs(opts):
    """
    support fetching from cvs sources in a local-sources mode

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        the fetched cache file; ``None`` if fetching has failed
    """

    assert opts._build_dir
    assert opts._local_srcs

    cache_dir = opts.cache_dir
    name = opts.name
    site = opts.site
    target_dir = opts._build_dir

    note('fetching {}...', name)

    cvsroot, module = _extract_site(site)
    if not cvsroot or not module:
        return None

    # cvs does not allow us to explicitly clone into a specific directory;
    # instead, adjust the working directory to where the folder will be held
    # and execute the checkout to specify the directory stem to use
    container_dir = os.path.dirname(target_dir)
    basename = os.path.basename(target_dir)

    # CVS requires the base directory exists before attempting to checkout
    verbose('preparing container directory')
    if not mkdir(container_dir):
        return None

    if not CVS.execute(['-d', cvsroot, 'checkout', '-d', basename, module],
            cwd=container_dir):
        err('unable to checkout module')
        return None

    return cache_dir


def _extract_site(site):
    """
    extracts the cvsroot and module from a configure site value

    When a CVS-specific site value is provided, it is combination of the
    CVSROOT and the module name (separated by a space). This call helps
    extract and returns the pair. If an issue is detected, an error is
    generated to the standard error string and `None` values are returned.

    Args:
        site: the site value

    Returns:
        tuple of the cvsroot and module
    """

    try:
        cvsroot, module = site.rsplit(' ', 1)
    except ValueError:
        err('''\
improper cvs site defined

The provided CVS site does not define both the CVSROOT as well as the target
module to checkout. For example:

    :pserver:anonymous@cvs.example.com:/var/lib/cvsroot mymodule

 Site: {}''', site)
        return None, None
    else:
        return cvsroot, module
