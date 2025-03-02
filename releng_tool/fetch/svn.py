# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.svn import SVN
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
import os
import tarfile


def fetch(opts):
    """
    support fetching from svn sources

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        the fetched cache content; ``None`` if fetching has failed
    """

    assert opts

    if not SVN.exists():
        err('unable to fetch package; svn is not installed')
        return None

    if opts._local_srcs:
        return fetch_local_srcs(opts)

    return fetch_default(opts)


def fetch_default(opts):
    """
    support fetching from svn sources in a default operating mode

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

    note(f'fetching {name}...')

    log('checking out sources')
    if not SVN.execute(['checkout', '-r', revision, site, work_dir],
            cwd=work_dir):
        err('unable to checkout module')
        return None

    log('caching sources')
    def svn_exclude(file):
        return file.endswith('.svn')

    # ensure cache file's directory exists
    cache_dir = os.path.abspath(os.path.join(cache_file, os.pardir))
    if not mkdir(cache_dir):
        return None

    with tarfile.open(cache_file, 'w:gz') as tar:
        tar.add(work_dir, arcname=name, exclude=svn_exclude)

    return cache_file


def fetch_local_srcs(opts):
    """
    support fetching from svn sources in a local-sources mode

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        the fetched cache directory; ``None`` if fetching has failed
    """

    assert opts._build_dir
    assert opts._local_srcs

    cache_dir = opts.cache_dir
    name = opts.name
    site = opts.site
    target_dir = opts._build_dir

    note('fetching {}...', name)

    if not SVN.execute(['checkout', site, target_dir]):
        err('unable to checkout module')
        return None

    return cache_dir
