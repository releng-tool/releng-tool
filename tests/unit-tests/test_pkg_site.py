# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import VcsType
from releng_tool.packages.site import site_vcs
from tests import RelengToolTestCase


class TestPkgSite(RelengToolTestCase):
    def test_pkg_site_vcs_type_brz(self):
        site, vcs = site_vcs('brz+example-brz-site')
        self.assertEqual(site, 'example-brz-site')
        self.assertEqual(vcs, VcsType.BRZ)

    def test_pkg_site_vcs_type_bzr(self):
        site, vcs = site_vcs('bzr+example-bzr-site')
        self.assertEqual(site, 'example-bzr-site')
        self.assertEqual(vcs, VcsType.BZR)

    def test_pkg_site_vcs_type_cvs(self):
        site, vcs = site_vcs('cvs+example-cvs-site')
        self.assertEqual(site, 'example-cvs-site')
        self.assertEqual(vcs, VcsType.CVS)

        val = ':pserver:anonymous@cvs.example.com:/var/lib/cvsroot mymodule'
        site, vcs = site_vcs(val)
        self.assertEqual(site, val)
        self.assertEqual(vcs, VcsType.CVS)

        val = ':ext:cvs@cvs.example.org:/usr/local/cvsroot mymodule'
        site, vcs = site_vcs(val)
        self.assertEqual(site, val)
        self.assertEqual(vcs, VcsType.CVS)

        val = ':extssh:cvs@cvs.example.org:/usr/local/cvsroot mymodule'
        site, vcs = site_vcs(val)
        self.assertEqual(site, val)
        self.assertEqual(vcs, VcsType.CVS)

        val = ':gserver:cvs@cvs.example.org:/usr/local/cvsroot mymodule'
        site, vcs = site_vcs(val)
        self.assertEqual(site, val)
        self.assertEqual(vcs, VcsType.CVS)

        val = ':kserver:cvs@cvs.example.org:/usr/local/cvsroot mymodule'
        site, vcs = site_vcs(val)
        self.assertEqual(site, val)
        self.assertEqual(vcs, VcsType.CVS)

    def test_pkg_site_vcs_type_file(self):
        site, vcs = site_vcs('file://example')
        self.assertEqual(site, 'file://example')
        self.assertEqual(vcs, VcsType.FILE)

        site, vcs = site_vcs('file+example-file-site')
        self.assertEqual(site, 'example-file-site')
        self.assertEqual(vcs, VcsType.FILE)

    def test_pkg_site_vcs_type_git(self):
        site, vcs = site_vcs('git+example-git-site')
        self.assertEqual(site, 'example-git-site')
        self.assertEqual(vcs, VcsType.GIT)

        site, vcs = site_vcs('example-git-site.git')
        self.assertEqual(site, 'example-git-site.git')
        self.assertEqual(vcs, VcsType.GIT)

    def test_pkg_site_vcs_type_hg(self):
        site, vcs = site_vcs('hg+example-hg-site')
        self.assertEqual(site, 'example-hg-site')
        self.assertEqual(vcs, VcsType.HG)

    def test_pkg_site_vcs_type_local(self):
        site, vcs = site_vcs('local')
        self.assertEqual(site, 'local')
        self.assertEqual(vcs, VcsType.LOCAL)

    def test_pkg_site_vcs_type_perforce(self):
        site, vcs = site_vcs('perforce+example-p4-site')
        self.assertEqual(site, 'example-p4-site')
        self.assertEqual(vcs, VcsType.PERFORCE)

        site, vcs = site_vcs('p4+example-p4-site')
        self.assertEqual(site, 'example-p4-site')
        self.assertEqual(vcs, VcsType.PERFORCE)

    def test_pkg_site_vcs_type_rsync(self):
        site, vcs = site_vcs('rsync+example-rsync-site')
        self.assertEqual(site, 'example-rsync-site')
        self.assertEqual(vcs, VcsType.RSYNC)

    def test_pkg_site_vcs_type_scp(self):
        site, vcs = site_vcs('scp+example-scp-site')
        self.assertEqual(site, 'example-scp-site')
        self.assertEqual(vcs, VcsType.SCP)

    def test_pkg_site_vcs_type_svn(self):
        site, vcs = site_vcs('svn+example-svn-site')
        self.assertEqual(site, 'example-svn-site')
        self.assertEqual(vcs, VcsType.SVN)

    def test_pkg_site_vcs_type_url(self):
        site, vcs = site_vcs('example.com')
        self.assertEqual(site, 'example.com')
        self.assertEqual(vcs, VcsType.URL)
