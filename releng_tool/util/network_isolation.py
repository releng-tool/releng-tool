# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from contextlib import contextmanager
import os
import socket


# isolate endpoint to use a local/free random port
LOCAL_RANDOM_PORT = ('127.0.0.1', 0)


@contextmanager
def network_isolate(*, enforce: bool = True):
    """
    attempt to isolate any network-related calls

    Provides a context which attempts to restrict any network-related calls.
    The goal is to help promote network-related actions during fetch stages
    to help improve support for offline builds for packages.

    This call will setup network proxy configurations which executables
    typically use (e.g. `https_proxy`). The proxy configurations will point to
    a local socket which does not accept connections. This should effectively
    deny network-related requests.

    Args:
        enforce (optional): whether to enforce isolation

    Yields:
        a context with restricted networking
    """

    # skip isolation if enforcement is off
    if not enforce:
        yield
        return

    # list of various proxy environment variables to configure
    entries = {
        'all_proxy': 'http://127.0.0.1:{port}',
        'ftp_proxy': 'http://127.0.0.1:{port}',
        'http_proxy': 'http://127.0.0.1:{port}',
        'https_proxy': 'http://127.0.0.1:{port}',
        'no_proxy': '',
        'rsync_proxy': '127.0.0.1:{port}',
    }

    # capture a list of any existing proxy settings that may be set
    old_env = {
        key: os.environ[key]
        for entry in entries
        for key in (entry.lower(), entry.upper())
        if key in os.environ
    }

    try:
        # build a socket to claim a specific port that we can use for
        # consuming network traffic
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(LOCAL_RANDOM_PORT)
            _, port = s.getsockname()

            # configure all proxy values
            for key, fmt in entries.items():
                if key == 'no_proxy':
                    continue
                new_proxy = fmt.format(port=port)
                os.environ[key] = new_proxy
                os.environ[key.upper()] = new_proxy

            # yield the context for any actions to be done
            yield
    finally:
        # clear any proxy values set
        for key in entries:
            os.environ.pop(key, None)
            os.environ.pop(key.upper(), None)

        # restore any original values
        os.environ.update(old_env)
