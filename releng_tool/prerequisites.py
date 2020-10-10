# -*- coding: utf-8 -*-
# Copyright 2020 releng-tool

from .defs import PackageType
from .defs import VcsType
from .tool.autoreconf import AUTORECONF
from .tool.bzr import BZR
from .tool.cmake import CMAKE
from .tool.cvs import CVS
from .tool.git import GIT
from .tool.hg import HG
from .tool.make import MAKE
from .tool.python import PYTHON
from .tool.python import PythonTool
from .tool.scp import SCP
from .tool.svn import SVN
from .util.log import err
from .util.log import verbose
import distutils.spawn

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

    def check(self, quiet=False):
        """
        check for the existence of required tools for the loaded package set

        For each loaded package, a series of required host tools will be checked
        and a caller will be notified whether or not anything is missing.

        Args:
            quiet (optional): whether or not to suppress output (defaults to
                ``False``)

        Returns:
            ``True`` is all known required tools exists; ``False`` otherwise
        """

        missing = set()
        pkg_types = set()
        python_interpreters = set()
        vcs_types = set()

        # package-defined requirements check
        for pkg in self.pkgs:
            pkg_types.add(pkg.type)
            vcs_types.add(pkg.vcs_type)

            if pkg.type == PackageType.AUTOTOOLS:
                if pkg.autotools_autoreconf:
                    if AUTORECONF.exists():
                        self._verbose_exists(AUTORECONF)
                    else:
                        missing.add(AUTORECONF.tool)

            elif pkg.type == PackageType.PYTHON:
                if pkg.python_interpreter:
                    python_tool = PythonTool(pkg.python_interpreter)
                else:
                    python_tool = PYTHON
                python_interpreters.add(python_tool)

        if PackageType.AUTOTOOLS in pkg_types:
            if MAKE.exists():
                self._verbose_exists(MAKE)
            else:
                missing.add(MAKE.tool)

        if PackageType.CMAKE in pkg_types:
            if CMAKE.exists():
                self._verbose_exists(CMAKE)
            else:
                missing.add(CMAKE.tool)

        if PackageType.PYTHON in pkg_types:
            for interpreter in python_interpreters:
                if interpreter.exists():
                    self._verbose_exists(interpreter)
                else:
                    missing.add(interpreter.tool)

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
            if distutils.spawn.find_executable(tool):
                verbose('prerequisite exists: ' + tool)
            else:
                missing.add(tool)

        if not quiet:
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
