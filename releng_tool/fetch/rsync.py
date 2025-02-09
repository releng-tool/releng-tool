# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.rsync import RSYNC
from releng_tool.util.io import interpret_stem_extension
from releng_tool.util.io import prepare_arguments
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.string import expand
import os
import tarfile


def fetch(opts):
    """
    support fetching from rsync sources

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
    work_dir = opts.work_dir

    cache_basename = os.path.basename(cache_file)
    cache_stem, __ = interpret_stem_extension(cache_basename)

    if not RSYNC.exists():
        err('unable to fetch package; rsync is not installed')
        return None

    note('fetching {}...', name)

    # options
    fetch_opts = {
        '--recursive': '',  # default recursive call
    }
    if opts.extra_opts:
        fetch_opts.update(expand(opts.extra_opts))

    # argument building
    fetch_args = [
    ]
    fetch_args.extend(prepare_arguments(fetch_opts))

    # sanity check provided arguments
    for fetch_arg in fetch_args:
        if '--remove-source-files' in fetch_arg:
            err('option `--remove-source-files` not permitted')
            return None

        if not fetch_arg.startswith('-'):
            err('invalid fetch option provided:', fetch_arg)
            return None

    fetch_args.append(site)  # source directory
    fetch_args.append(work_dir)  # destination directory

    if not RSYNC.execute(fetch_args, cwd=work_dir):
        err('unable to rsync from source')
        return None
    log('successfully invoked rsync for source')

    with tarfile.open(cache_file, 'w:gz') as tar:
        tar.add(work_dir, arcname=cache_stem)

    return cache_file
