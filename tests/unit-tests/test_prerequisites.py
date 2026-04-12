# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PackageType
from releng_tool.defs import PythonSetupType
from releng_tool.defs import VcsType
from releng_tool.packages.package import RelengPackage
from releng_tool.prerequisites import RelengPrerequisites
from releng_tool.tool.python import PYTHON
from unittest.mock import patch
from tests import RelengToolTestCase


PFX = 'releng_tool.prerequisites'


class TestPrerequisites(RelengToolTestCase):
    def setUp(self):
        self.pkg = RelengPackage('test', '1.0')

    def test_prerequisites_exclude(self):
        prerequisites = RelengPrerequisites([], ['misc-command'])
        check = prerequisites.check(exclude=['misc-command'])
        self.assertTrue(check)

    def test_prerequisites_exist(self):
        # python should exist; since we rely on python
        prerequisites = RelengPrerequisites([], [PYTHON.tool])
        check = prerequisites.check()
        self.assertTrue(check)

    def test_prerequisites_missing(self):
        prerequisites = RelengPrerequisites([], ['unknown-command-releng'])
        check = prerequisites.check()
        self.assertFalse(check)

    @patch(f'{PFX}.AUTORECONF.exists', new=lambda: True)
    @patch(f'{PFX}.MAKE.exists', new=lambda: True)
    def test_prerequisites_uc_autoreconf_exists(self):
        self.pkg.type = PackageType.AUTOTOOLS
        self.pkg.autotools_autoreconf = True
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.AUTORECONF.exists', new=lambda: False)
    @patch(f'{PFX}.MAKE.exists', new=lambda: True)
    def test_prerequisites_uc_autoreconf_missing(self):
        self.pkg.type = PackageType.AUTOTOOLS
        self.pkg.autotools_autoreconf = True
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.MAKE.exists', new=lambda: True)
    def test_prerequisites_uc_autotools_make_exists(self):
        self.pkg.type = PackageType.AUTOTOOLS
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.MAKE.exists', new=lambda: False)
    def test_prerequisites_uc_autotools_make_missing(self):
        self.pkg.type = PackageType.AUTOTOOLS
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.BRZ.exists', new=lambda: True)
    def test_prerequisites_uc_brz_exists(self):
        self.pkg.vcs_type = VcsType.BRZ
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.BRZ.exists', new=lambda: False)
    def test_prerequisites_uc_brz_missing(self):
        self.pkg.vcs_type = VcsType.BRZ
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.CARGO.exists', new=lambda: True)
    def test_prerequisites_uc_cargo_exists(self):
        self.pkg.type = PackageType.CARGO
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.CARGO.exists', new=lambda: False)
    def test_prerequisites_uc_cargo_missing(self):
        self.pkg.type = PackageType.CARGO
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.CMAKE.exists', new=lambda: True)
    def test_prerequisites_uc_cmake_exists(self):
        self.pkg.type = PackageType.CMAKE
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.CMAKE.exists', new=lambda: False)
    def test_prerequisites_uc_cmake_missing(self):
        self.pkg.type = PackageType.CMAKE
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.CVS.exists', new=lambda: True)
    def test_prerequisites_uc_cvs_exists(self):
        self.pkg.vcs_type = VcsType.CVS
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.CVS.exists', new=lambda: False)
    def test_prerequisites_uc_cvs_missing(self):
        self.pkg.vcs_type = VcsType.CVS
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.GIT.exists', new=lambda: True)
    def test_prerequisites_uc_git_exists(self):
        self.pkg.vcs_type = VcsType.GIT
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.GIT.exists', new=lambda: False)
    def test_prerequisites_uc_git_missing(self):
        self.pkg.vcs_type = VcsType.GIT
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.HG.exists', new=lambda: True)
    def test_prerequisites_uc_hg_exists(self):
        self.pkg.vcs_type = VcsType.HG
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.HG.exists', new=lambda: False)
    def test_prerequisites_uc_hg_missing(self):
        self.pkg.vcs_type = VcsType.HG
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.MAKE.exists', new=lambda: True)
    def test_prerequisites_uc_make_exists(self):
        self.pkg.type = PackageType.MAKE
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.MAKE.exists', new=lambda: False)
    def test_prerequisites_uc_make_missing(self):
        self.pkg.type = PackageType.MAKE
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.MESON.exists', new=lambda: True)
    def test_prerequisites_uc_meson_exists(self):
        self.pkg.type = PackageType.MESON
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.MESON.exists', new=lambda: False)
    def test_prerequisites_uc_meson_missing(self):
        self.pkg.type = PackageType.MESON
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.GIT.exists', new=lambda: True)
    def test_prerequisites_uc_perforce_git_exists(self):
        self.pkg.vcs_type = VcsType.PERFORCE
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.GIT.exists', new=lambda: False)
    def test_prerequisites_uc_perforce_git_missing(self):
        self.pkg.vcs_type = VcsType.PERFORCE
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec', new=lambda *_args: True)
    def test_prerequisites_uc_python_installer_exists(self):
        self.pkg.type = PackageType.PYTHON
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec')
    def test_prerequisites_uc_python_installer_missing(self, mfs):
        def find_spec(name):
            return name != 'installer'
        mfs.side_effect = find_spec

        self.pkg.type = PackageType.PYTHON
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec', new=lambda *_args: True)
    def test_prerequisites_uc_python_interpreter_exists(self):
        self.pkg.type = PackageType.PYTHON
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: False)
    @patch(f'{PFX}.importlib.util.find_spec', new=lambda *_args: True)
    def test_prerequisites_uc_python_interpreter_missing(self):
        self.pkg.type = PackageType.PYTHON
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec', new=lambda *_args: True)
    def test_prerequisites_uc_python_pt_flit_exists(self):
        self.pkg.type = PackageType.PYTHON
        self.pkg.python_setup_type = PythonSetupType.FLIT
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec')
    def test_prerequisites_uc_python_pt_flit_missing(self, mfs):
        def find_spec(name):
            return name != 'flit_core.wheel'
        mfs.side_effect = find_spec

        self.pkg.type = PackageType.PYTHON
        self.pkg.python_setup_type = PythonSetupType.FLIT
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec', new=lambda *_args: True)
    def test_prerequisites_uc_python_pt_hatch_exists(self):
        self.pkg.type = PackageType.PYTHON
        self.pkg.python_setup_type = PythonSetupType.HATCH
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec')
    def test_prerequisites_uc_python_pt_hatch_missing(self, mfs):
        def find_spec(name):
            return name != 'hatch'
        mfs.side_effect = find_spec

        self.pkg.type = PackageType.PYTHON
        self.pkg.python_setup_type = PythonSetupType.HATCH
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec', new=lambda *_args: True)
    def test_prerequisites_uc_python_pt_pdm_exists(self):
        self.pkg.type = PackageType.PYTHON
        self.pkg.python_setup_type = PythonSetupType.PDM
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec')
    def test_prerequisites_uc_python_pt_pdm_missing(self, mfs):
        def find_spec(name):
            return name != 'pdm'
        mfs.side_effect = find_spec

        self.pkg.type = PackageType.PYTHON
        self.pkg.python_setup_type = PythonSetupType.PDM
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec', new=lambda *_args: True)
    def test_prerequisites_uc_python_pt_pep517_build_exists(self):
        self.pkg.type = PackageType.PYTHON
        self.pkg.python_setup_type = PythonSetupType.PEP517
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec')
    def test_prerequisites_uc_python_pt_pep517_build_missing(self, mfs):
        def find_spec(name):
            return name != 'build'
        mfs.side_effect = find_spec

        self.pkg.type = PackageType.PYTHON
        self.pkg.python_setup_type = PythonSetupType.PEP517
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec', new=lambda *_args: True)
    def test_prerequisites_uc_python_pt_poetry_exists(self):
        self.pkg.type = PackageType.PYTHON
        self.pkg.python_setup_type = PythonSetupType.POETRY
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec')
    def test_prerequisites_uc_python_pt_poetry_missing(self, mfs):
        def find_spec(name):
            return name != 'poetry'
        mfs.side_effect = find_spec

        self.pkg.type = PackageType.PYTHON
        self.pkg.python_setup_type = PythonSetupType.POETRY
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec', new=lambda *_args: True)
    def test_prerequisites_uc_python_pt_setuptools_exists(self):
        self.pkg.type = PackageType.PYTHON
        self.pkg.python_setup_type = PythonSetupType.SETUPTOOLS
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.PYTHON.exists', new=lambda: True)
    @patch(f'{PFX}.importlib.util.find_spec')
    def test_prerequisites_uc_python_pt_setuptools_missing(self, mfs):
        def find_spec(name):
            return name != 'setuptools'
        mfs.side_effect = find_spec

        self.pkg.type = PackageType.PYTHON
        self.pkg.python_setup_type = PythonSetupType.SETUPTOOLS
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.RSYNC.exists', new=lambda: True)
    def test_prerequisites_uc_rsync_exists(self):
        self.pkg.vcs_type = VcsType.RSYNC
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.RSYNC.exists', new=lambda: False)
    def test_prerequisites_uc_rsync_missing(self):
        self.pkg.vcs_type = VcsType.RSYNC
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.SCONS.exists', new=lambda: True)
    def test_prerequisites_uc_scons_exists(self):
        self.pkg.type = PackageType.SCONS
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.SCONS.exists', new=lambda: False)
    def test_prerequisites_uc_scons_missing(self):
        self.pkg.type = PackageType.SCONS
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.SCP.exists', new=lambda: True)
    def test_prerequisites_uc_scp_exists(self):
        self.pkg.vcs_type = VcsType.SCP
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.SCP.exists', new=lambda: False)
    def test_prerequisites_uc_scp_missing(self):
        self.pkg.vcs_type = VcsType.SCP
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.SVN.exists', new=lambda: True)
    def test_prerequisites_uc_svn_exists(self):
        self.pkg.vcs_type = VcsType.SVN
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.SVN.exists', new=lambda: False)
    def test_prerequisites_uc_svn_missing(self):
        self.pkg.vcs_type = VcsType.SVN
        self._assertPackagePrerequisite(expected=False)

    @patch(f'{PFX}.WAF.exists', new=lambda: True)
    def test_prerequisites_uc_waf_exists(self):
        self.pkg.type = PackageType.WAF
        self._assertPackagePrerequisite(expected=True)

    @patch(f'{PFX}.WAF.exists', new=lambda: False)
    def test_prerequisites_uc_waf_missing(self):
        self.pkg.type = PackageType.WAF
        self._assertPackagePrerequisite(expected=False)

    def _assertPackagePrerequisite(self, *, expected: bool):
        prerequisites = RelengPrerequisites([self.pkg], [])
        check = prerequisites.check()
        self.assertEqual(check, expected)
