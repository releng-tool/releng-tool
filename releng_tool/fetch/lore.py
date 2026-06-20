# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.lore import LORE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io_tar import tar_cachefile
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.string import expand


def fetch(opts):
    """
    support fetching from lore sources

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
    work_dir = opts.work_dir

    if not LORE.exists():
        err('unable to fetch package; lore is not installed')
        return None

    note(f'fetching {name}...')

    # options
    fetch_opts = {
        '--direct-file-write': '',
    }
    if opts.extra_opts:
        fetch_opts.update(expand(opts.extra_opts))

    # argument building
    LORE_HASH_LEN = 64
    rev_arg = '--revision' if len(revision) == LORE_HASH_LEN else '--branch'

    fetch_args = [
        'clone',
        site,
        work_dir,
        rev_arg,
        revision,
    ]
    fetch_args.extend(prepare_arguments(fetch_opts))

    log('checking out sources')
    if not LORE.execute(fetch_args, cwd=work_dir):
        err('unable to clone sources')
        return None

    log('caching sources')
    if not tar_cachefile(work_dir, cache_file, name, '.lore'):
        return None

    return cache_file
