# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.hg import HG
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
import os


def fetch(opts):
    """
    support fetching from mercurial sources

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        the fetched cache directory; ``None`` if fetching has failed
    """

    assert opts

    if not HG.exists():
        err('unable to fetch package; hg (mercurial) is not installed')
        return None

    if opts._local_srcs:
        return fetch_local_srcs(opts)

    return fetch_default(opts)


def fetch_default(opts):
    """
    support fetching from mercurial sources in a default operating mode

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        the fetched cache directory; ``None`` if fetching has failed
    """

    cache_dir = opts.cache_dir
    name = opts.name
    revision = opts.revision
    site = opts.site

    hg_dir = ['--repository', cache_dir]

    # check if we have the target revision; if so, full stop
    if os.path.isdir(cache_dir) and not opts.ignore_cache:
        if HG.execute([*hg_dir, '--quiet', 'log', '--rev', revision],
                cwd=cache_dir, quiet=True):
            return cache_dir

    note('fetching {}...', name)

    # if we have no cache for this repository, build one
    if not os.path.isdir(cache_dir) or len(os.listdir(cache_dir)) == 0:
        if not mkdir(cache_dir):
            return None

        if not HG.execute(['--noninteractive', '--verbose',
                'clone', '--noupdate', site, cache_dir],
                cwd=cache_dir):
            err('unable to clone mercurial repository')
            return None

    log('fetching most recent sources')
    if not HG.execute([*hg_dir, '--noninteractive', '--verbose', 'pull'],
            cwd=cache_dir):
        err('unable to fetch from remote repository')
        return None

    log('verifying target revision exists')
    if not HG.execute([*hg_dir, '--quiet', 'log', '--rev', revision],
            cwd=cache_dir, quiet=True):
        err('unable to find matching revision in repository: {}\n'
            ' (revision: {})', name, revision)
        return None

    return cache_dir


def fetch_local_srcs(opts):
    """
    support fetching from mercurial sources in a local-sources mode

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

    if not HG.execute(['--verbose', 'clone', site, target_dir]):
        err('unable to clone mercurial repository')
        return None

    return cache_dir
