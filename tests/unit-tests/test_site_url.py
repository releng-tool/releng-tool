# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool
from releng_tool.tool.tar import TAR
from releng_tool.tool.tar import TAR_COMMAND
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests.support import fetch_unittest_assets_dir
from tests.support.http_daemon import httpd_context
import io
import os
import tarfile
import unittest


class TestSiteUrl(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        # support skipping the test for a distribution build
        if os.getenv('RELENG_SKIP_TEST_SITE_URL'):
            raise unittest.SkipTest('skipped due to environment flag')

    def setUp(self):
        os.environ.pop('all_proxy', None)
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)

    def test_site_url_fetch_archive_tar_bz2_valid(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.tar.bz2'

            httpd_assets = fetch_unittest_assets_dir('sample-files')
            archive = os.path.join(httpd_assets, 'sample-files.tar.bz2')

            with open(archive, 'rb') as f:
                data = f.read()

            httpd.rsp.append((200, data))

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertTrue(rv)

                outdir = os.environ['MINIMAL_BUILD_DIR']
                stripped_file = os.path.join(outdir, 'bz2-file-container.txt')

                self.assertTrue(os.path.exists(stripped_file))

    def test_site_url_fetch_archive_tar_invalid(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.tgz'

            httpd.rsp.append((200, b'not-an-archive'))

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertFalse(rv)

    def test_site_url_fetch_archive_tar_path_traversal(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/traversal.tar'

            dummy_file_data = io.BytesIO(b'test')
            dummy_file_sz = len(dummy_file_data.getvalue())

            data = io.BytesIO()
            with tarfile.open(fileobj=data, mode='w') as tar:
                test = tarfile.TarInfo('../test')
                test.size = dummy_file_sz
                tar.addfile(test, dummy_file_data)

            httpd.rsp.append((200, data.getvalue()))

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                otes = TAR.exists()
                try:
                    # temporarily force the internal tar processing
                    RelengTool.detected[TAR_COMMAND] = False

                    rv = engine.run()
                finally:
                    RelengTool.detected[TAR_COMMAND] = otes

                self.assertFalse(rv)

    def test_site_url_fetch_archive_tar_valid_external_extract(self):
        if not TAR.exists():
            raise unittest.SkipTest('environment does not have a tar command')

        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.tar'

            httpd_assets = fetch_unittest_assets_dir('sample-files')
            archive = os.path.join(httpd_assets, 'sample-files.tar')

            with open(archive, 'rb') as f:
                data = f.read()

            httpd.rsp.append((200, data))

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertTrue(rv)

                outdir = os.environ['MINIMAL_BUILD_DIR']
                stripped_file = os.path.join(outdir, 'tar-file-container.txt')

                self.assertTrue(os.path.exists(stripped_file))

    def test_site_url_fetch_archive_tar_valid_internal_extract(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.tar'

            httpd_assets = fetch_unittest_assets_dir('sample-files')
            archive = os.path.join(httpd_assets, 'sample-files.tar')

            with open(archive, 'rb') as f:
                data = f.read()

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                otes = TAR.exists()
                try:
                    # temporarily force a non-external tar command (if needed)
                    RelengTool.detected[TAR_COMMAND] = False

                    httpd.rsp.append((200, data))
                    rv = engine.run()
                finally:
                    RelengTool.detected[TAR_COMMAND] = otes

                self.assertTrue(rv)

                outdir = os.environ['MINIMAL_BUILD_DIR']
                stripped_file = os.path.join(outdir, 'tar-file-container.txt')

                self.assertTrue(os.path.exists(stripped_file))

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                # redo tar fetch but with a no strip option
                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')
                    f.write('MINIMAL_STRIP_COUNT=0\n')

                try:
                    RelengTool.detected[TAR_COMMAND] = False

                    httpd.rsp.append((200, data))
                    rv = engine.run()
                finally:
                    RelengTool.detected[TAR_COMMAND] = otes

                self.assertTrue(rv)

                outdir = os.environ['MINIMAL_BUILD_DIR']
                sample_root_file = os.path.join(outdir, 'tar-file-root')
                container_dir = os.path.join(outdir, 'container')
                sample_container_file = os.path.join(
                    container_dir, 'tar-file-container.txt')

                self.assertTrue(os.path.exists(sample_root_file))
                self.assertTrue(os.path.exists(sample_container_file))

    def test_site_url_fetch_archive_tgz_valid(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.tgz'

            httpd_assets = fetch_unittest_assets_dir('sample-files')
            archive = os.path.join(httpd_assets, 'sample-files.tgz')

            with open(archive, 'rb') as f:
                data = f.read()

            httpd.rsp.append((200, data))

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertTrue(rv)

                outdir = os.environ['MINIMAL_BUILD_DIR']
                stripped_file = os.path.join(outdir, 'tgz-file-container.txt')

                self.assertTrue(os.path.exists(stripped_file))

    def test_site_url_fetch_archive_txz_valid(self):
        if not TAR.exists():
            raise unittest.SkipTest('environment does not have a tar command')

        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.tar.xz'

            httpd_assets = fetch_unittest_assets_dir('sample-files')
            archive = os.path.join(httpd_assets, 'sample-files.tar.xz')

            with open(archive, 'rb') as f:
                data = f.read()

            httpd.rsp.append((200, data))

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertTrue(rv)

                outdir = os.environ['MINIMAL_BUILD_DIR']
                stripped_file = os.path.join(outdir, 'txz-file-container.txt')

                self.assertTrue(os.path.exists(stripped_file))

    def test_site_url_fetch_archive_zip_invalid(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.zip'

            httpd.rsp.append((200, b'not-an-archive'))

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertFalse(rv)

    def test_site_url_fetch_archive_zip_valid(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.zip'

            httpd_assets = fetch_unittest_assets_dir('sample-files')
            archive = os.path.join(httpd_assets, 'sample-files.zip')

            with open(archive, 'rb') as f:
                data = f.read()

            httpd.rsp.append((200, data))

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertTrue(rv)

    def test_site_url_fetch_file_http(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.txt'

            httpd.rsp.append((200, b'Sample text file.'))

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertTrue(rv)

    def test_site_url_fetch_file_https(self):
        with httpd_context(secure=True) as httpd:
            host, port = httpd.server_address
            site = f'https://localhost:{port}/test.txt'

            httpd.rsp.append((200, b'Sample text file.'))

            with prepare_testenv(template='https-self-signed') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir, 'package', 'pkg', 'pkg.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'PKG_SITE="{site}"\n')

                rv = engine.run()
                self.assertTrue(rv)

    def test_site_url_fetch_missing(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/missing.txt'

            httpd.rsp.append((404, None))

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertFalse(rv)

    def test_site_url_fetch_retry(self):
        with httpd_context() as httpd:
            host, port = httpd.server_address
            site = f'http://{host}:{port}/test.txt'

            httpd.rsp.append((503, None))  # first attempt fails
            httpd.rsp.append((200, b'Sample text file.'))  # retry attempt

            with prepare_testenv(template='minimal') as engine:
                root_dir = engine.opts.root_dir
                pkg_script = os.path.join(root_dir,
                    'package', 'minimal', 'minimal.rt')
                self.assertTrue(os.path.exists(pkg_script))

                with open(pkg_script, 'a') as f:
                    f.write(f'MINIMAL_SITE="{site}"\n')

                rv = engine.run()
                self.assertTrue(rv)
