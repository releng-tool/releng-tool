# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.git import GIT
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
import os
import tarfile


def fetch(opts):
    """
    support fetching from perforce sources

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

    if not GIT.exists():
        err('unable to fetch package; git (for perforce) is not installed')
        return None

    note(f'fetching {name}...')

    p4env = {}

    try:
        p4root, view_dir = site.rsplit(' ', 1)
    except ValueError:
        err('''\
improper perforce site defined

The provided Perforce site does not define both the Perforce service as well
as the depot path to synchronize. For example:

    perforce+guest@tcp4:p4.example.com:1666 //my-srcs

 Site: {}''', site)
        return None

    # check if there is a user defined in the root; if so, extract
    if '@' in p4root:
        p4user, p4root = p4root.rsplit('@', 1)
        if p4user:
            p4env['P4USER'] = p4user

    # configure the service to use
    p4env['P4PORT'] = p4root

    log('checking out sources')
    if revision:
        target_path = f'{view_dir}@{revision}'
    else:
        target_path = view_dir
    if not GIT.execute(['p4', 'clone', target_path],
            cwd=work_dir, env=p4env):
        err('unable to clone sources')
        return None

    log('caching sources')

    # ensure cache file's directory exists
    cache_dir = os.path.abspath(os.path.join(cache_file, os.pardir))
    if not mkdir(cache_dir):
        return None

    def perforce_filter(info):
        if info.name.endswith('.git'):
            return None
        return info

    with tarfile.open(cache_file, 'w:gz') as tar:
        tar.add(work_dir, arcname=name, filter=perforce_filter)

    return cache_file
