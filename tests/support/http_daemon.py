# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from tests.support import fetch_unittest_assets_dir
from threading import Thread
import os
import ssl
import time


# http server endpoint to use a local/free random port
LOCAL_RANDOM_PORT = ('127.0.0.1', 0)


class MockServerRequestHandler(BaseHTTPRequestHandler):
    """
    mock server request handler

    Provides a handler for managing HTTP requests and responses for unit
    testing.
    """

    def do_GET(self):
        self._track_request('GET')
        self._process_rsp()

    def do_HEAD(self):
        self._track_request('HEAD')
        self._process_rsp()

    def do_POST(self):
        self._track_request('POST')
        self._process_rsp()

    def do_PUT(self):
        self._track_request('PUT')
        self._process_rsp()

    def _process_rsp(self):
        try:
            code, data = self.server.rsp.pop(0)
        except IndexError:
            code = 501
            data = None

        self.send_response(code)
        self.end_headers()
        if data:
            self.wfile.write(data)

    def _track_request(self, action):
        requests = self.server.req.setdefault(action, [])
        requests.append((self.path, dict(self.headers)))


def build_httpd(secure=None):
    """
    build an http daemon

    Builds an HTTP server instance on a random local port which can be used
    to verify HTTP/HTTPS request handling for various releng-tool features.
    By default, an HTTP is spawned with `secure` set to `False`. When building
    a "secure" HTTP server, key/cert. files are used from the assets folder.

    Args:
        secure (optional): whether or not a secure http server should be made

    Returns:
        the http server
    """

    httpd = HTTPServer(LOCAL_RANDOM_PORT, MockServerRequestHandler)
    httpd.req = {}
    httpd.rsp = []

    if secure:
        keyfile, certfile = fetch_cert_files()

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile, keyfile=keyfile)

        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    return httpd


def fetch_cert_files():
    """
    find certificate files for unit testing

    Returns a tuple of a key file and certificate file used to create a
    unit testing "secure" HTTP server. Dummy pem files are included in the
    testing asserts folder, which this call can return the paths to these
    files.

    Returns:
        2-tuple of a key file and certificate file
    """

    httpd_assets = fetch_unittest_assets_dir('httpd')
    keyfile = os.path.join(httpd_assets, 'test-notprivate-key-pem')
    certfile = os.path.join(httpd_assets, 'test-cert-pem')
    return keyfile, certfile


@contextmanager
def httpd_context(secure=None):
    """
    create an http daemon context

    Builds a context-enabled HTTP server instance on a random local port which
    can be used to verify HTTP/HTTPS request handling for various releng-tool
    features. The build HTTP server is served by an internally managed thread.
    By default, an HTTP is spawned with `secure` set to `False`. When building
    a "secure" HTTP server, key/cert. files are used from the assets folder.

    Args:
        secure (optional): whether or not a secure http server should be made

    Yields:
        the http server
    """

    httpd = None
    httpd_thread = None

    try:
        httpd = build_httpd(secure=secure)

        # start accepting requests
        def serve_forever(httpd):
            httpd.serve_forever()

        httpd_thread = Thread(target=serve_forever, args=(httpd,))
        httpd_thread.start()

        # yield context for a moment to help threads to ready up
        time.sleep(0)

        yield httpd

    finally:
        if httpd_thread:
            httpd.shutdown()
            httpd_thread.join()

        httpd.server_close()
