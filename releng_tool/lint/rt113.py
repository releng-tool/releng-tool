# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.lint import LintState
from releng_tool.packages import pkg_key
from releng_tool.packages.package import RelengPackage
from releng_tool.defs import VcsType
from releng_tool.packages.site import site_vcs
import ast


def rt113(state: LintState, pkg: RelengPackage, nodes: list[ast.AST]):
    """
    linting git-only configurations

    Args:
        state: the linting state
        pkg: the active package
        node: node being processed
    """

    # before checking for conditional ways the vcs-type would be set, perform
    # the simple check with the package instance
    if pkg.vcs_type == VcsType.GIT:
        return

    site_key = pkg_key(pkg.name, Rpk.SITE)
    vcs_type_key = pkg_key(pkg.name, Rpk.VCS_TYPE)

    # first, ensure we have no scenario where git is a possible vcs type
    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == site_key:
                if isinstance(node.value, ast.Constant):
                    _, pkg_vcs_type = site_vcs(node.value.value)
                    if pkg_vcs_type == VcsType.GIT:
                        return

            if isinstance(target, ast.Name) and target.id == vcs_type_key:
                if isinstance(node.value, ast.Constant):
                    if node.value.value == VcsType.GIT:
                        return

    # confirmed no git vcs type -- check for any type-specific configs
    msg = 'unexpected key for non-git-vcs package'
    key_checks = [
        pkg_key(pkg.name, Rpk.GIT_CONFIG),
        pkg_key(pkg.name, Rpk.GIT_DEPTH),
        pkg_key(pkg.name, Rpk.GIT_REFSPECS),
        pkg_key(pkg.name, Rpk.GIT_SUBMODULES),
        pkg_key(pkg.name, Rpk.GIT_VERIFY_REVISION),
    ]

    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name):
                for key_check in key_checks:
                    if target.id == key_check:
                        state.report(
                            113, pkg.def_file, node,
                            f'{msg}: {key_check}',
                        )
                        break
