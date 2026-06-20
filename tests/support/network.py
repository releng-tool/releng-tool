# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from urllib.request import ProxyHandler
from urllib.request import build_opener
import os


def fetch_http_file_proxy_enforced(site: str) -> int:
    """
    fetch a local http file through a forced proxy

    This call helps perform a ``urlopen`` capability that enforces configured
    environment proxies for local sites. Python automatically ignores proxies
    for local url fetches, and some tests may want to override this.

    Args:
        site: the site to fetch

    Returns:
        the http status (if any)
    """

    proxy_opts = {}
    if 'http_proxy' in os.environ:
        proxy_opts['http'] = os.environ['http_proxy']
    proxy_handler = ProxyHandler(proxy_opts)
    proxy_opener = build_opener(proxy_handler)

    DEFAULT_TIMEOUT = 1
    with proxy_opener.open(site, timeout=DEFAULT_TIMEOUT) as rsp:
        return rsp.status
