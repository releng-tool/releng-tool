# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PackageType
from releng_tool.defs import VcsType
from releng_tool.tool.autoreconf import AUTORECONF
from releng_tool.tool.autoreconf import AUTORECONF_COMMAND
from releng_tool.tool.brz import BRZ
from releng_tool.tool.bzr import BZR
from releng_tool.tool.cargo import CARGO
from releng_tool.tool.cmake import CMAKE
from releng_tool.tool.cvs import CVS
from releng_tool.tool.git import GIT
from releng_tool.tool.hg import HG
from releng_tool.tool.make import MAKE
from releng_tool.tool.meson import MESON
from releng_tool.tool.python import PYTHON
from releng_tool.tool.python import PythonTool
from releng_tool.tool.rsync import RSYNC
from releng_tool.tool.scons import SCONS
from releng_tool.tool.scp import SCP
from releng_tool.tool.svn import SVN
from releng_tool.util.log import err
from releng_tool.util.log import verbose
from shutil import which
import importlib.util


class RelengPrerequisites:
    """
    releng tool's prerequisites check helper

    Each package may require a specific host tool instead. For example, a
    project referencing a Git source will require the ``git`` command line tool.
    A user may not know they are missing a tool until the releng-tool process
    reaches the point where the tool needs to be invoked. This utility helps
    promote a fail-fast approach by pre-checking possible tools needed by each
    loaded package and notifying a user before attempting to start.

    Args:
        pkgs: the packages to check for prerequisites
        tools: the tools to check for existence

    Attributes:
        pkgs: the packages to check for prerequisites
        tools: the tools to check for existence
    """
    def __init__(self, pkgs, tools):
        self.pkgs = pkgs
        self.tools = tools

    def check(self, quiet=False, exclude=None):
        """
        check for the existence of required tools for the loaded package set

        For each loaded package, a series of required host tools will be checked
        and a caller will be notified whether or not anything is missing.

        Args:
            quiet (optional): whether or not to suppress output (defaults to
                ``False``)
            exclude (optional): which tools to exclude from this check

        Returns:
            ``True`` is all known required tools exists; ``False`` otherwise
        """

        exclude = exclude if exclude else []
        missing = set()
        pkg_types = set()
        python_interpreters = set()
        vcs_types = set()

        # package-defined requirements check
        for pkg in self.pkgs:
            if pkg.type not in exclude:
                pkg_types.add(pkg.type)
            if pkg.vcs_type not in exclude:
                vcs_types.add(pkg.vcs_type)

            if pkg.type == PackageType.AUTOTOOLS:
                if pkg.autotools_autoreconf:
                    if AUTORECONF_COMMAND not in exclude:
                        if AUTORECONF.exists():
                            self._verbose_exists(AUTORECONF)
                        else:
                            missing.add(AUTORECONF.tool)

            elif pkg.type == PackageType.PYTHON:
                if pkg.python_interpreter:
                    if pkg.python_interpreter not in exclude:
                        python_tool = PythonTool(pkg.python_interpreter)
                        python_interpreters.add(python_tool)
                else:
                    python_interpreters.add(PYTHON)

        if PackageType.AUTOTOOLS in pkg_types or PackageType.MAKE in pkg_types:
            if MAKE.exists():
                self._verbose_exists(MAKE)
            else:
                missing.add(MAKE.tool)

        if PackageType.CARGO in pkg_types:
            if CARGO.exists():
                self._verbose_exists(CARGO)
            else:
                missing.add(CARGO.tool)

        if PackageType.CMAKE in pkg_types:
            if CMAKE.exists():
                self._verbose_exists(CMAKE)
            else:
                missing.add(CMAKE.tool)

        if PackageType.MESON in pkg_types:
            if MESON.exists():
                self._verbose_exists(MESON)
            else:
                missing.add(MESON.tool)

        if PackageType.PYTHON in pkg_types:
            for interpreter in python_interpreters:
                if interpreter.exists():
                    self._verbose_exists(interpreter)
                else:
                    missing.add(interpreter.tool)

            has_installer = importlib.util.find_spec('installer')
            if not has_installer:
                missing.add('python-installer')

        if PackageType.SCONS in pkg_types:
            if SCONS.exists():
                self._verbose_exists(SCONS)
            else:
                missing.add(SCONS.tool)

        if VcsType.BRZ in vcs_types:
            if BRZ.exists():
                self._verbose_exists(BRZ)
            else:
                missing.add(BRZ.tool)

        if VcsType.BZR in vcs_types:
            if BZR.exists():
                self._verbose_exists(BZR)
            else:
                missing.add(BZR.tool)

        if VcsType.CVS in vcs_types:
            if CVS.exists():
                self._verbose_exists(CVS)
            else:
                missing.add(CVS.tool)

        if VcsType.GIT in vcs_types:
            if GIT.exists():
                self._verbose_exists(GIT)
            else:
                missing.add(GIT.tool)

        if VcsType.HG in vcs_types:
            if HG.exists():
                self._verbose_exists(HG)
            else:
                missing.add(HG.tool)

        if VcsType.PERFORCE in vcs_types:
            if GIT.exists():
                self._verbose_exists(GIT)
            else:
                missing.add(GIT.tool)

        if VcsType.RSYNC in vcs_types:
            if RSYNC.exists():
                self._verbose_exists(RSYNC)
            else:
                missing.add(RSYNC.tool)

        if VcsType.SCP in vcs_types:
            if SCP.exists():
                self._verbose_exists(SCP)
            else:
                missing.add(SCP.tool)

        if VcsType.SVN in vcs_types:
            if SVN.exists():
                self._verbose_exists(SVN)
            else:
                missing.add(SVN.tool)

        # project-provided tools check
        for tool in self.tools:
            if tool not in exclude:
                if which(tool):
                    verbose('prerequisite exists: ' + tool)
                else:
                    missing.add(tool)

        if missing and not quiet:
            sorted_missing = list(missing)
            sorted_missing.sort()

            msg = 'missing the following host tools for this project:'
            msg += '\n'
            msg += '\n'
            for entry in sorted_missing:
                msg += ' ' + entry + '\n'
            err(msg)

        return len(missing) == 0

    def _verbose_exists(self, tool):
        """
        verbose log that a provided tool exists

        Will generate a verbose log which will indicate to a user that a
        provided tool has been detected on the host system.

        Args:
            tool: the tool
        """
        verbose('prerequisite exists: ' + tool.tool)
