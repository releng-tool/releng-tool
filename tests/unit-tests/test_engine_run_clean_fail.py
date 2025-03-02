# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import GlobalAction
from releng_tool.defs import PkgAction
from tests import RelengToolTestCase
from tests import mock_os_remove_permission_denied
from tests import prepare_testenv
from tests import prepare_workdir as wd
from tests import redirect_stdout
from tests import run_testenv
import os


TEMPLATE = 'minimal'


class TestEngineRunCleanFail(RelengToolTestCase):
    def run(self, result=None):
        with wd() as cache_dir, wd() as dl_dir, wd() as out_dir:
            self.config = {
                'cache_dir': cache_dir,
                'dl_dir': dl_dir,
                'out_dir': out_dir,
            }

            with self.env_wrap(), redirect_stdout() as _:
                with prepare_testenv(
                        config=self.config, template=TEMPLATE) as engine:
                    rv = engine.run()
                    self.assertTrue(rv)

                    self.opts = engine.opts
                    self.pkg_build_dir = os.path.join(
                        engine.opts.build_dir, TEMPLATE + '-v1.0')
                    self.pkg_ff_prefix = os.path.join(
                        self.pkg_build_dir, '.releng_tool-stage-')

            super().run(result)

    def test_engine_run_clean_fail_noperm_all_clean(self):
        with mock_os_remove_permission_denied():
            self.config['action'] = GlobalAction.CLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_all_distclean(self):
        with mock_os_remove_permission_denied():
            self.config['action'] = GlobalAction.DISTCLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_all_mrproper(self):
        with mock_os_remove_permission_denied():
            self.config['action'] = GlobalAction.MRPROPER
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_build_dir_clean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.build_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.CLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_build_dir_distclean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.build_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.DISTCLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_build_dir_mrproper(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.build_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.MRPROPER
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_cache_dir_distclean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.cache_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.DISTCLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_dl_dir_distclean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.dl_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.DISTCLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_force(self):
        file_flags = [
            self.pkg_ff_prefix + 'bootstrap',
            self.pkg_ff_prefix + 'build',
            self.pkg_ff_prefix + 'configure',
            self.pkg_ff_prefix + 'install',
            self.pkg_ff_prefix + 'post',
        ]

        for target_file in file_flags:
            def rmcmd(path, **kwargs):  # noqa: ARG001
                if str(path) == target_file:  # noqa: B023
                    raise OSError('Mocked permission denied')

            with mock_os_remove_permission_denied(f=rmcmd):
                self.config['force'] = True
                rv = run_testenv(config=self.config, template=TEMPLATE)
                self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_host_dir_clean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.host_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.CLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_host_dir_distclean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.host_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.DISTCLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_host_dir_mrproper(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.host_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.MRPROPER
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_license_dir_clean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.license_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.CLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_license_dir_distclean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.license_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.DISTCLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_license_dir_mrproper(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.license_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.MRPROPER
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_pkg_clean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.pkg_build_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = TEMPLATE + '-' + PkgAction.CLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_pkg_distclean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.pkg_build_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = TEMPLATE + '-' + PkgAction.DISTCLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_pkg_flags_rebuild(self):
        file_flags = [
            self.pkg_ff_prefix + 'build',
            self.pkg_ff_prefix + 'install',
            self.pkg_ff_prefix + 'post',
        ]

        for target_file in file_flags:
            def rmcmd(path, **kwargs):  # noqa: ARG001
                if str(path) == target_file:  # noqa: B023
                    raise OSError('Mocked permission denied')

            with mock_os_remove_permission_denied(f=rmcmd):
                self.config['action'] = TEMPLATE + '-' + PkgAction.REBUILD
                rv = run_testenv(config=self.config, template=TEMPLATE)
                self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_pkg_flags_reconfigure(self):
        file_flags = [
            self.pkg_ff_prefix + 'bootstrap',
            self.pkg_ff_prefix + 'build',
            self.pkg_ff_prefix + 'configure',
            self.pkg_ff_prefix + 'install',
            self.pkg_ff_prefix + 'post',
        ]

        for target_file in file_flags:
            def rmcmd(path, **kwargs):  # noqa: ARG001
                if str(path) == target_file:  # noqa: B023
                    raise OSError('Mocked permission denied')

            with mock_os_remove_permission_denied(f=rmcmd):
                self.config['action'] = TEMPLATE + '-' + PkgAction.RECONFIGURE
                rv = run_testenv(config=self.config, template=TEMPLATE)
                self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_pkg_flags_reinstall(self):
        file_flags = [
            self.pkg_ff_prefix + 'install',
            self.pkg_ff_prefix + 'post',
        ]

        for target_file in file_flags:
            def rmcmd(path, **kwargs):  # noqa: ARG001
                if str(path) == target_file:  # noqa: B023
                    raise OSError('Mocked permission denied')

            with mock_os_remove_permission_denied(f=rmcmd):
                self.config['action'] = TEMPLATE + '-' + PkgAction.REINSTALL
                rv = run_testenv(config=self.config, template=TEMPLATE)
                self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_staging_dir_clean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.staging_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.CLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_staging_dir_distclean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.staging_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.DISTCLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_staging_dir_mrproper(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.staging_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.MRPROPER
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_symbols_dir_clean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.symbols_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.CLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_symbols_dir_distclean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.symbols_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.DISTCLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_symbols_dir_mrproper(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.symbols_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.MRPROPER
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_target_dir_clean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.target_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.CLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_target_dir_distclean(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.target_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.DISTCLEAN
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_fail_noperm_check_target_dir_mrproper(self):
        def rmcmd(path, **kwargs):  # noqa: ARG001
            if str(path) == self.opts.target_dir:
                raise OSError('Mocked permission denied')

        with mock_os_remove_permission_denied(f=rmcmd):
            self.config['action'] = GlobalAction.MRPROPER
            rv = run_testenv(config=self.config, template=TEMPLATE)
            self.assertFalse(rv)

    def test_engine_run_clean_success_clean(self):
        self.config['action'] = GlobalAction.CLEAN
        rv = run_testenv(config=self.config, template=TEMPLATE)
        self.assertTrue(rv)

    def test_engine_run_clean_success_distclean(self):
        self.config['action'] = GlobalAction.DISTCLEAN
        rv = run_testenv(config=self.config, template=TEMPLATE)
        self.assertTrue(rv)

    def test_engine_run_clean_success_mrproper(self):
        self.config['action'] = GlobalAction.MRPROPER
        rv = run_testenv(config=self.config, template=TEMPLATE)
        self.assertTrue(rv)
