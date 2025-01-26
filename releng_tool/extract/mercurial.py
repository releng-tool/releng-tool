# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.hg import HG
from releng_tool.util.log import err
from releng_tool.util.log import log


def extract(opts):
    """
    support extraction (checkout) of a mercurial cache into a build directory

    With provided extraction options (``RelengExtractOptions``), the extraction
    stage will be processed. A Mercurial extraction process will populate a
    working tree based off the cached Mercurial repository acquired from the
    fetch stage.

    Args:
        opts: the extraction options

    Returns:
        ``True`` if the extraction stage is completed; ``False`` otherwise
    """

    assert opts
    cache_dir = opts.cache_dir
    revision = opts.revision
    work_dir = opts.work_dir

    if not HG.exists():
        err('unable to extract package; mercurial (hg) is not installed')
        return None

    log(f'checking out revision ({revision}) into work tree')
    if not HG.execute(['--verbose', 'clone', '--rev', revision,
            cache_dir, work_dir],
            cwd=work_dir):
        err('unable to checkout revision')
        return False

    return True
