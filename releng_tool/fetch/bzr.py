# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.bzr import BZR
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
import os

try:
    CERTIFI_MISSING_WARNED = False
    import certifi
except ImportError:
    certifi = None


def fetch(opts):
    """
    support fetching from bzr sources

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

    if not BZR.exists():
        err('unable to fetch package; bzr is not installed')
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

    # some environments may have issue export bzr sources due to certificate
    # issues; this quirk allows injecting certifi-provided certificates for
    # all bzr exports
    if 'releng.bzr.certifi' in opts._quirks:
        global CERTIFI_MISSING_WARNED

        if certifi:
            verbose('performing bzr fetch with certifi certificates')
            pkg_site = certifi.where()
            export_opts.append('-Ossl.ca_certs=' + pkg_site)
        elif not CERTIFI_MISSING_WARNED:
            CERTIFI_MISSING_WARNED = True
            warn('''\
unable to perform bzr fetch with certifi certificates

A quirk has been enabled to export bzr images using certifi
certificates; however, certifi is not installed on this system.
''')

    log('exporting sources')
    if not BZR.execute(export_opts, poll=True):
        err('unable to export module')
        return None

    return cache_file
