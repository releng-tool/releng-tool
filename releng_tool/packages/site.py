# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import VcsType


def site_vcs(site):
    """
    return a resolved site and its vcs type from a site value

    This call accepts a site value and returns both the resolved site value
    and the detected VCS type for this site. For example:

        https://github.com/releng-tool/releng-tool.git

    Will return a site value of ``git@github.com:releng-tool/releng-tool.git``
    with a VCS type of ``VcsType.GIT``. If a site-prefixed is used, it will
    be removed from the resolved site value. For example:

        git+git@github.com:releng-tool/releng-tool.git

    Will return a site value of ``git@github.com:releng-tool/releng-tool.git``
    with a VCS type of ``VcsType.GIT``.

    Args:
        site: the site value

    Returns:
        tuple of the resolved site and vcs type
    """

    site_lc = site.lower()

    if site_lc.startswith('brz+'):
        site = site.removeprefix('brz+')
        vcs_type = VcsType.BRZ
    elif site_lc.startswith('bzr+'):
        site = site.removeprefix('bzr+')
        vcs_type = VcsType.BZR
    elif site_lc.startswith('cvs+'):
        site = site.removeprefix('cvs+')
        vcs_type = VcsType.CVS
    elif site_lc.startswith((
            ':ext:',
            ':extssh:',
            ':gserver:',
            ':kserver:',
            ':pserver:',
            )):
        vcs_type = VcsType.CVS
    elif site_lc.startswith('file://'):
        vcs_type = VcsType.FILE
    elif site_lc.startswith('file+'):
        site = site.removeprefix('file+')
        vcs_type = VcsType.FILE
    elif site_lc.startswith('git+'):
        site = site.removeprefix('git+')
        vcs_type = VcsType.GIT
    elif site_lc.endswith('.git'):
        vcs_type = VcsType.GIT
    elif site_lc.startswith('hg+'):
        site = site.removeprefix('hg+')
        vcs_type = VcsType.HG
    elif site_lc.startswith('p4+'):
        site = site.removeprefix('p4+')
        vcs_type = VcsType.PERFORCE
    elif site_lc.startswith('perforce+'):
        site = site.removeprefix('perforce+')
        vcs_type = VcsType.PERFORCE
    elif site_lc.startswith('rsync+'):
        site = site.removeprefix('rsync+')
        vcs_type = VcsType.RSYNC
    elif site_lc.startswith('scp+'):
        site = site.removeprefix('scp+')
        vcs_type = VcsType.SCP
    elif site_lc.startswith('svn+'):
        site = site.removeprefix('svn+')
        vcs_type = VcsType.SVN
    elif site_lc == 'local':
        vcs_type = VcsType.LOCAL
    else:
        vcs_type = VcsType.URL

    return site, vcs_type
