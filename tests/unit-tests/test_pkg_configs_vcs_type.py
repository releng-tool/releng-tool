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

        pkg = self.LOAD('vcs-type-devmode-override', manager=manager).package
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
        pkg = self.LOAD('missing').package

        self.assertEqual(pkg.vcs_type, VcsType.NONE)

    def test_pkgconfig_vcs_type_valid_brz_explicit(self):
        pkg = self.LOAD('vcs-type-valid-brz-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.BRZ)

    def test_pkgconfig_vcs_type_valid_brz_implicit(self):
        pkg = self.LOAD('vcs-type-valid-brz-implicit').package
        self.assertEqual(pkg.vcs_type, VcsType.BRZ)

    def test_pkgconfig_vcs_type_valid_bzr_explicit(self):
        pkg = self.LOAD('vcs-type-valid-bzr-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.BZR)

    def test_pkgconfig_vcs_type_valid_bzr_implicit(self):
        pkg = self.LOAD('vcs-type-valid-bzr-implicit').package
        self.assertEqual(pkg.vcs_type, VcsType.BZR)

    def test_pkgconfig_vcs_type_valid_cvs_explicit(self):
        pkg = self.LOAD('vcs-type-valid-cvs-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

    def test_pkgconfig_vcs_type_valid_cvs_implicit(self):
        pkg = self.LOAD('vcs-type-valid-cvs-implicit').package
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

        pkg = self.LOAD('vcs-type-valid-cvs-implicit2').package
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

        pkg = self.LOAD('vcs-type-valid-cvs-implicit3').package
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

        pkg = self.LOAD('vcs-type-valid-cvs-implicit4').package
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

        pkg = self.LOAD('vcs-type-valid-cvs-implicit5').package
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

        pkg = self.LOAD('vcs-type-valid-cvs-implicit6').package
        self.assertEqual(pkg.vcs_type, VcsType.CVS)

    def test_pkgconfig_vcs_type_valid_file_deprecated(self):
        pkg = self.LOAD('vcs-type-valid-file-deprecated-url').package
        self.assertEqual(pkg.vcs_type, VcsType.FILE)

    def test_pkgconfig_vcs_type_valid_file_explicit(self):
        pkg = self.LOAD('vcs-type-valid-file-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.FILE)

    def test_pkgconfig_vcs_type_valid_file_implicit(self):
        pkg = self.LOAD('vcs-type-valid-file-implicit').package
        self.assertEqual(pkg.vcs_type, VcsType.FILE)

    def test_pkgconfig_vcs_type_valid_git_explicit(self):
        pkg = self.LOAD('vcs-type-valid-git-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.GIT)

    def test_pkgconfig_vcs_type_valid_git_implicit(self):
        pkg = self.LOAD('vcs-type-valid-git-implicit1').package
        self.assertEqual(pkg.vcs_type, VcsType.GIT)

        pkg = self.LOAD('vcs-type-valid-git-implicit2').package
        self.assertEqual(pkg.vcs_type, VcsType.GIT)

    def test_pkgconfig_vcs_type_valid_hg_explicit(self):
        pkg = self.LOAD('vcs-type-valid-hg-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.HG)

    def test_pkgconfig_vcs_type_valid_hg_implicit(self):
        pkg = self.LOAD('vcs-type-valid-hg-implicit').package
        self.assertEqual(pkg.vcs_type, VcsType.HG)

    def test_pkgconfig_vcs_type_valid_local_explicit(self):
        pkg = self.LOAD('vcs-type-valid-local-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.LOCAL)

    def test_pkgconfig_vcs_type_valid_local_implicit(self):
        pkg = self.LOAD('vcs-type-valid-local-implicit').package
        self.assertEqual(pkg.vcs_type, VcsType.LOCAL)

    def test_pkgconfig_vcs_type_valid_none_explicit(self):
        pkg = self.LOAD('vcs-type-valid-none-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.NONE)

    def test_pkgconfig_vcs_type_valid_none_implicit(self):
        pkg = self.LOAD('vcs-type-valid-none-implicit').package
        self.assertEqual(pkg.vcs_type, VcsType.NONE)

    def test_pkgconfig_vcs_type_valid_perforce_explicit(self):
        pkg = self.LOAD('vcs-type-valid-perforce-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.PERFORCE)

    def test_pkgconfig_vcs_type_valid_perforce_implicit(self):
        pkg = self.LOAD('vcs-type-valid-perforce-implicit').package
        self.assertEqual(pkg.vcs_type, VcsType.PERFORCE)

        pkg = self.LOAD('vcs-type-valid-perforce-implicit2').package
        self.assertEqual(pkg.vcs_type, VcsType.PERFORCE)

    def test_pkgconfig_vcs_type_valid_rsync_explicit(self):
        pkg = self.LOAD('vcs-type-valid-rsync-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.RSYNC)

    def test_pkgconfig_vcs_type_valid_rsync_implicit(self):
        pkg = self.LOAD('vcs-type-valid-rsync-implicit').package
        self.assertEqual(pkg.vcs_type, VcsType.RSYNC)

    def test_pkgconfig_vcs_type_valid_scp_explicit(self):
        pkg = self.LOAD('vcs-type-valid-scp-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.SCP)

    def test_pkgconfig_vcs_type_valid_scp_implicit(self):
        pkg = self.LOAD('vcs-type-valid-scp-implicit').package
        self.assertEqual(pkg.vcs_type, VcsType.SCP)

    def test_pkgconfig_vcs_type_valid_svn_explicit(self):
        pkg = self.LOAD('vcs-type-valid-svn-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.SVN)

    def test_pkgconfig_vcs_type_valid_svn_implicit(self):
        pkg = self.LOAD('vcs-type-valid-svn-implicit').package
        self.assertEqual(pkg.vcs_type, VcsType.SVN)

    def test_pkgconfig_vcs_type_valid_url_explicit(self):
        pkg = self.LOAD('vcs-type-valid-url-explicit').package
        self.assertEqual(pkg.vcs_type, VcsType.URL)

    def test_pkgconfig_vcs_type_valid_url_implicit(self):
        pkg = self.LOAD('vcs-type-valid-url-implicit').package
        self.assertEqual(pkg.vcs_type, VcsType.URL)
