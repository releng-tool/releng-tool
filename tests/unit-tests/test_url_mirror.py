# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests.support.http_daemon import httpd_context
import os
import unittest


class TestUrlMirror(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        # support skipping the test for a distribution build
        if os.getenv('RELENG_SKIP_TEST_URL_MIRROR'):
            raise unittest.SkipTest('skipped due to environment flag')

    def setUp(self):
        os.environ.pop('all_proxy', None)
        os.environ.pop('http_proxy', None)

    def test_url_mirror_fallback_default(self):
        with httpd_context() as httpd, httpd_context() as mirror_httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.txt'

            mirror_host, mirror_port = mirror_httpd.server_address
            mirror = f'http://{mirror_host}:{mirror_port}/'

            httpd.rsp.append((200, b'Sample text file.'))
            mirror_httpd.rsp.append((404, None))

            with prepare_testenv(template='minimal') as engine:
                root_dir = Path(engine.opts.root_dir)

                prj_def = root_dir / 'releng-tool.rt'
                self.assertTrue(prj_def.is_file())

                with prj_def.open('a') as f:
                    f.write(f'url_mirror = "{mirror}"\n')

                pkg_script = root_dir / 'package' / 'minimal' / 'minimal.rt'
                self.assertTrue(pkg_script.is_file())

                with pkg_script.open('a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertTrue(rv)

                dl_dir = Path(engine.opts.dl_dir)
                pkg_artifact = dl_dir / 'minimal' / 'minimal-v1.0.txt'

                self.assertTrue(pkg_artifact.is_file())

                self.assertEqual(len(httpd.req), 1)
                self.assertEqual(len(httpd.rsp), 0)
                self.assertEqual(len(mirror_httpd.req), 1)
                self.assertEqual(len(mirror_httpd.rsp), 0)

    def test_url_mirror_fallback_restricted(self):
        with httpd_context() as httpd, httpd_context() as mirror_httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.txt'

            mirror_host, mirror_port = mirror_httpd.server_address
            mirror = f'http://{mirror_host}:{mirror_port}/'

            httpd.rsp.append((200, b'Sample text file.'))  # should not hit
            mirror_httpd.rsp.append((404, None))

            with prepare_testenv(template='minimal') as engine:
                # force only-mirror mode
                engine.opts.only_mirror = True

                root_dir = Path(engine.opts.root_dir)

                prj_def = root_dir / 'releng-tool.rt'
                self.assertTrue(prj_def.is_file())

                with prj_def.open('a') as f:
                    f.write(f'url_mirror = "{mirror}"\n')

                pkg_script = root_dir / 'package' / 'minimal' / 'minimal.rt'
                self.assertTrue(pkg_script.is_file())

                with pkg_script.open('a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertFalse(rv)

                self.assertEqual(len(httpd.req), 0)
                self.assertEqual(len(httpd.rsp), 1)
                self.assertEqual(len(mirror_httpd.req), 1)
                self.assertEqual(len(mirror_httpd.rsp), 0)

    def test_url_mirror_pkg_hint(self):
        with httpd_context() as httpd, httpd_context() as mirror_httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.txt'

            mirror_host, mirror_port = mirror_httpd.server_address
            mirror = f'http://{mirror_host}:{mirror_port}/{{name}}/{{version}}/'

            mirror_httpd.rsp.append((200, b'Sample text file.'))
            httpd.rsp.append((500, None))  # should not hit

            with prepare_testenv(template='minimal') as engine:
                root_dir = Path(engine.opts.root_dir)

                prj_def = root_dir / 'releng-tool.rt'
                self.assertTrue(prj_def.is_file())

                with prj_def.open('a') as f:
                    f.write(f'url_mirror = "{mirror}"\n')

                pkg_script = root_dir / 'package' / 'minimal' / 'minimal.rt'
                self.assertTrue(pkg_script.is_file())

                with pkg_script.open('a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertTrue(rv)

                dl_dir = Path(engine.opts.dl_dir)
                pkg_artifact = dl_dir / 'minimal' / 'minimal-v1.0.txt'

                self.assertTrue(pkg_artifact.is_file())

                self.assertEqual(len(httpd.req), 0)
                self.assertEqual(len(httpd.rsp), 1)
                self.assertEqual(len(mirror_httpd.req), 1)
                self.assertEqual(len(mirror_httpd.rsp), 0)

                self.assertIn('GET', mirror_httpd.req)

                get_calls = mirror_httpd.req['GET']
                self.assertEqual(len(get_calls), 1)

                req_url, _ = get_calls[0]
                self.assertEqual(req_url, '/minimal/v1.0/minimal-v1.0.txt')

    def test_url_mirror_used(self):
        with httpd_context() as httpd, httpd_context() as mirror_httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.txt'

            mirror_host, mirror_port = mirror_httpd.server_address
            mirror = f'http://{mirror_host}:{mirror_port}/'

            mirror_httpd.rsp.append((200, b'Sample text file.'))
            httpd.rsp.append((500, None))  # should not hit

            with prepare_testenv(template='minimal') as engine:
                root_dir = Path(engine.opts.root_dir)

                prj_def = root_dir / 'releng-tool.rt'
                self.assertTrue(prj_def.is_file())

                with prj_def.open('a') as f:
                    f.write(f'url_mirror = "{mirror}"\n')

                pkg_script = root_dir / 'package' / 'minimal' / 'minimal.rt'
                self.assertTrue(pkg_script.is_file())

                with pkg_script.open('a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertTrue(rv)

                dl_dir = Path(engine.opts.dl_dir)
                pkg_artifact = dl_dir / 'minimal' / 'minimal-v1.0.txt'

                self.assertTrue(pkg_artifact.is_file())

                self.assertEqual(len(httpd.req), 0)
                self.assertEqual(len(httpd.rsp), 1)
                self.assertEqual(len(mirror_httpd.req), 1)
                self.assertEqual(len(mirror_httpd.rsp), 0)
