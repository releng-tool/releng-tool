# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.util.network_isolation import network_isolate
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
from tests import setprjcfg
from tests.support.http_daemon import httpd_context
from tests.support.network import fetch_http_file_proxy_enforced
from urllib.error import URLError
import os
import unittest


class TestNetworkIsolation(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        # support skipping the test for a distribution build
        if os.getenv('RELENG_SKIP_TEST_NETWORK_ISOLATION'):
            raise unittest.SkipTest('skipped due to environment flag')

    def test_netiso_engine_default(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.txt'
            os.environ['RELENG_TEST_NETWORK_ISOLATION_SITE'] = site

            # queue three files for configure, build and install stages
            httpd.rsp.append((200, b'Sample text file.'))
            httpd.rsp.append((200, b'Sample text file.'))
            httpd.rsp.append((200, b'Sample text file.'))

            with prepare_testenv(template='stage-network-events') as engine:
                rv = engine.run()
                self.assertTrue(rv)

    def test_netiso_engine_enforced_package(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.txt'
            os.environ['RELENG_TEST_NETWORK_ISOLATION_SITE'] = site

            with prepare_testenv(template='stage-network-events') as engine:
                setpkgcfg(engine, 'test', Rpk.NETWORK_ISOLATION, value=True)

                rv = engine.run()
                self.assertFalse(rv)

    def test_netiso_engine_enforced_project(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.txt'
            os.environ['RELENG_TEST_NETWORK_ISOLATION_SITE'] = site

            with prepare_testenv(template='stage-network-events') as engine:
                setprjcfg(engine, 'network_isolation', value=True)

                rv = engine.run()
                self.assertFalse(rv)

    def test_netiso_engine_unenforced_project(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.txt'
            os.environ['RELENG_TEST_NETWORK_ISOLATION_SITE'] = site

            # queue three files for configure, build and install stages
            httpd.rsp.append((200, b'Sample text file.'))
            httpd.rsp.append((200, b'Sample text file.'))
            httpd.rsp.append((200, b'Sample text file.'))

            with prepare_testenv(template='stage-network-events') as engine:
                setpkgcfg(engine, 'test', Rpk.NETWORK_ISOLATION, value=False)
                setprjcfg(engine, 'network_isolation', value=True)

                rv = engine.run()
                self.assertTrue(rv)

    def test_netiso_util_enforced(self):
        with httpd_context() as httpd, network_isolate():
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.txt'

            httpd.rsp.append((200, b'Sample text file.'))

            with self.assertRaises(URLError):
                fetch_http_file_proxy_enforced(site)

    def test_netiso_util_not_enforced(self):
        with httpd_context() as httpd, network_isolate(enforce=False):
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.txt'

            httpd.rsp.append((200, b'Sample text file.'))

            status = fetch_http_file_proxy_enforced(site)
            self.assertEqual(status, 200)

    def test_netiso_util_proxy_restored(self):
        expected_proxy = 'dummy-proxy-value'

        os.environ['http_proxy'] = expected_proxy
        os.environ['HTTPS_PROXY'] = expected_proxy
        os.environ.pop('ftp_proxy', None)

        with network_isolate():
            self.assertNotEqual(os.environ['http_proxy'], expected_proxy)
            self.assertNotEqual(os.environ['HTTPS_PROXY'], expected_proxy)

        self.assertEqual(os.environ['http_proxy'], expected_proxy)
        self.assertEqual(os.environ['HTTPS_PROXY'], expected_proxy)
        self.assertFalse('ftp_proxy' in os.environ)
