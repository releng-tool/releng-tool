# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from releng_tool.defs import VcsType
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.exceptions import RelengToolMissingPackageSite
from releng_tool.packages.exceptions import RelengToolUnknownVcsType
from tests.support.pkg_config_test import TestPkgConfigsBase

class TestPkgConfigsVcsType(TestPkgConfigsBase):
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

    def test_pkgconfig_vcs_type_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertEqual(pkg.vcs_type, VcsType.NONE)

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
