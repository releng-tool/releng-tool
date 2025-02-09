# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io_copy import path_copy
from releng_tool.util.log import debug
from releng_tool.util.log import note
from urllib.request import url2pathname


def fetch(opts):
    """
    support fetching from a file path

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
    site = opts.site

    note('fetching {}...', name)

    file_url = site.removeprefix('file://')
    file_path = url2pathname(file_url)

    debug(f'attempting to copy file: {file_path} | {cache_file}')
    if not path_copy(file_path, cache_file, critical=False):
        return None

    debug('completed copy')
    return cache_file
