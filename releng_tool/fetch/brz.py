# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.brz import BRZ
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
import os


def fetch(opts):
    """
    support fetching from brz sources

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        the fetched cache file; ``None`` if fetching has failed
    """

    assert opts
    cache_file = opts.cache_file
    name = opts.name
    revision = opts.revision
    site = opts.site

    if not BRZ.exists():
        err('unable to fetch package; brz is not installed')
        return None

    note('fetching {}...', name)

    cache_dir = os.path.abspath(os.path.join(cache_file, os.pardir))
    if not mkdir(cache_dir):
        return None

    export_opts = [
        'export',
        cache_file,
        site,
        '--format=tgz',
        '--root=' + name,
        '--revision=' + revision,
    ]

    log('exporting sources')
    if not BRZ.execute(export_opts, poll=True):
        err('unable to export module')
        return None

    return cache_file
