# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import VcsType
from releng_tool.opts import RelengEngineOptions
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.exceptions import RelengToolMissingPackageRevision
from releng_tool.packages.exceptions import RelengToolMissingPackageSite
from releng_tool.packages.exceptions import RelengToolUnknownVcsType
from releng_tool.packages.manager import RelengPackageManager
from releng_tool.registry import RelengRegistry
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsVcsType(TestPkgConfigsBase):
    def test_pkgconfig_vcs_type_devmode_override(self):
        opts = RelengEngineOptions()
        opts.devmode = 'override'

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg, _, _ = self.LOAD('vcs-type-devmode-override', manager=manager)
        self.assertEqual(pkg.vcs_type, VcsType.BZR)

    def test_pkgconfig_vcs_type_invalid_brz(self):
        with self.assertRaises(RelengToolMissingPackageSite):
            self.LOAD('vcs-type-invalid-brz-nosite')

    def test_pkgconfig_vcs_type_invalid_bzr(self):
        with self.assertRaises(RelengToolMissingPackageSite):
            self.LOAD('vcs-type-invalid-bzr-nosite')

    def test_pkgconfig_vcs_type_invalid_cvs(self):
        with self.assertRaises(RelengToolMissingPackageSite):
            self.LOAD('vcs-type-invalid-cvs-nosite')

    def test_pkgconfig_vcs_type_invalid_git(self):
        with self.assertRaises(RelengToolMissingPackageSite):
            self.LOAD('vcs-type-invalid-git-nosite')

    def test_pkgconfig_vcs_type_invalid_hg(self):
        with self.assertRaises(RelengToolMissingPackageSite):
            self.LOAD('vcs-type-invalid-hg-nosite')

    def test_pkgconfig_vcs_type_invalid_perforce(self):
        with self.assertRaises(RelengToolMissingPackageSite):
            self.LOAD('vcs-type-invalid-perforce-nosite')

    def test_pkgconfig_vcs_type_invalid_rsync(self):
        with self.assertRaises(RelengToolMissingPackageSite):
            self.LOAD('vcs-type-invalid-rsync-nosite')

    def test_pkgconfig_vcs_type_invalid_scp(self):
        with self.assertRaises(RelengToolMissingPackageSite):
            self.LOAD('vcs-type-invalid-scp-nosite')

    def test_pkgconfig_vcs_type_invalid_svn(self):
        with self.assertRaises(RelengToolMissingPackageSite):
            self.LOAD('vcs-type-invalid-svn-nosite')

    def test_pkgconfig_vcs_type_invalid_type(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('vcs-type-invalid-type')

    def test_pkgconfig_vcs_type_invalid_url(self):
        with self.assertRaises(RelengToolMissingPackageSite):
            self.LOAD('vcs-type-invalid-url-nosite')

    def test_pkgconfig_vcs_type_invalid_value(self):
        with self.assertRaises(RelengToolUnknownVcsType):
            self.LOAD('vcs-type-invalid-value')

    def test_pkgconfig_vcs_type_missing_revision_brz(self):
        with self.assertRaises(RelengToolMissingPackageRevision):
            self.LOAD('vcs-type-invalid-brz-norevision')

    def test_pkgconfig_vcs_type_missing_revision_bzr(self):
        with self.assertRaises(RelengToolMissingPackageRevision):
            self.LOAD('vcs-type-invalid-bzr-norevision')

    def test_pkgconfig_vcs_type_missing_revision_cvs(self):
        with self.assertRaises(RelengToolMissingPackageRevision):
            self.LOAD('vcs-type-invalid-cvs-norevision')

    def test_pkgconfig_vcs_type_missing_revision_git(self):
        with self.assertRaises(RelengToolMissingPackageRevision):
            self.LOAD('vcs-type-invalid-git-norevision')

    def test_pkgconfig_vcs_type_missing_revision_hg(self):
        with self.assertRaises(RelengToolMissingPackageRevision):
            self.LOAD('vcs-type-invalid-hg-norevision')

    def test_pkgconfig_vcs_type_missing_revision_svn(self):
        with self.assertRaises(RelengToolMissingPackageRevision):
            self.LOAD('vcs-type-invalid-svn-norevision')

    def test_pkgconfig_vcs_type_missing_site(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertEqual(pkg.vcs_type, VcsType.NONE)

    def test_pkgconfig_vcs_type_valid_brz_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-brz-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.BRZ)

    def test_pkgconfig_vcs_type_valid_brz_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-brz-implicit')
        self.assertEqual(pkg.vcs_type, VcsType.BRZ)

    def test_pkgconfig_vcs_type_valid_bzr_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-bzr-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.BZR)

    def test_pkgconfig_vcs_type_valid_bzr_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-bzr-implicit')
        self.assertEqual(pkg.vcs_type, VcsType.BZR)

    def test_pkgconfig_vcs_type_valid_cvs_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-cvs-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

    def test_pkgconfig_vcs_type_valid_cvs_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-cvs-implicit')
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

        pkg, _, _ = self.LOAD('vcs-type-valid-cvs-implicit2')
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

        pkg, _, _ = self.LOAD('vcs-type-valid-cvs-implicit3')
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

        pkg, _, _ = self.LOAD('vcs-type-valid-cvs-implicit4')
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

        pkg, _, _ = self.LOAD('vcs-type-valid-cvs-implicit5')
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

        pkg, _, _ = self.LOAD('vcs-type-valid-cvs-implicit6')
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

    def test_pkgconfig_vcs_type_valid_file_deprecated(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-file-deprecated-url')
        self.assertEqual(pkg.vcs_type, VcsType.FILE)

    def test_pkgconfig_vcs_type_valid_file_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-file-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.FILE)

    def test_pkgconfig_vcs_type_valid_file_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-file-implicit')
        self.assertEqual(pkg.vcs_type, VcsType.FILE)

    def test_pkgconfig_vcs_type_valid_git_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-git-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.GIT)

    def test_pkgconfig_vcs_type_valid_git_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-git-implicit1')
        self.assertEqual(pkg.vcs_type, VcsType.GIT)

        pkg, _, _ = self.LOAD('vcs-type-valid-git-implicit2')
        self.assertEqual(pkg.vcs_type, VcsType.GIT)

    def test_pkgconfig_vcs_type_valid_hg_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-hg-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.HG)

    def test_pkgconfig_vcs_type_valid_hg_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-hg-implicit')
        self.assertEqual(pkg.vcs_type, VcsType.HG)

    def test_pkgconfig_vcs_type_valid_local_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-local-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.LOCAL)

    def test_pkgconfig_vcs_type_valid_local_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-local-implicit')
        self.assertEqual(pkg.vcs_type, VcsType.LOCAL)

    def test_pkgconfig_vcs_type_valid_none_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-none-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.NONE)

    def test_pkgconfig_vcs_type_valid_none_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-none-implicit')
        self.assertEqual(pkg.vcs_type, VcsType.NONE)

    def test_pkgconfig_vcs_type_valid_perforce_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-perforce-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.PERFORCE)

    def test_pkgconfig_vcs_type_valid_perforce_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-perforce-implicit')
        self.assertEqual(pkg.vcs_type, VcsType.PERFORCE)

        pkg, _, _ = self.LOAD('vcs-type-valid-perforce-implicit2')
        self.assertEqual(pkg.vcs_type, VcsType.PERFORCE)

    def test_pkgconfig_vcs_type_valid_rsync_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-rsync-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.RSYNC)

    def test_pkgconfig_vcs_type_valid_rsync_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-rsync-implicit')
        self.assertEqual(pkg.vcs_type, VcsType.RSYNC)

    def test_pkgconfig_vcs_type_valid_scp_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-scp-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.SCP)

    def test_pkgconfig_vcs_type_valid_scp_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-scp-implicit')
        self.assertEqual(pkg.vcs_type, VcsType.SCP)

    def test_pkgconfig_vcs_type_valid_svn_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-svn-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.SVN)

    def test_pkgconfig_vcs_type_valid_svn_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-svn-implicit')
        self.assertEqual(pkg.vcs_type, VcsType.SVN)

    def test_pkgconfig_vcs_type_valid_url_explicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-url-explicit')
        self.assertEqual(pkg.vcs_type, VcsType.URL)

    def test_pkgconfig_vcs_type_valid_url_implicit(self):
        pkg, _, _ = self.LOAD('vcs-type-valid-url-implicit')
        self.assertEqual(pkg.vcs_type, VcsType.URL)
