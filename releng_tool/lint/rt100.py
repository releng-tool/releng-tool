# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.lint import LintState
from releng_tool.packages.package import RelengPackage
import ast


def rt100(state: LintState, pkg: RelengPackage, node: ast.AST):
    """
    perform linting "100" -- unexpected package configuration

    Args:
        state: the linting state
        pkg: the active package
        node: node being processed
    """

    # only check assignments/left-side -- as users may try to use
    # configuration hints from other packages to configure options
    # of another package
    if not isinstance(node, ast.Name) or not isinstance(node.ctx, ast.Store):
        return

    # ignore exact matched configurations
    supported_pkg_opts = state.pkgkey_opts[pkg]
    if node.id in supported_pkg_opts:
        return

    # check if this variable is named with a suffix matching
    # known package configuration suffixes; if so, check the
    # variable does match an expected package key -- if it
    # does not, most likely an invalid key entry:
    #  LIBFOOO_VERSION -> LIBFOO_VERSION
    for suffix in state.pkgkey_suffixes:
        if not node.id.endswith(suffix):
            continue

        state.report(
            100, pkg.def_file, node,
            f'unexpected package configuration: {node.id}',
        )
        return

    # check if a supported package option is a subset of this
    # node identifier:
    #  LIBFOO_VERSIONN -> LIBFOO_VERSION
    for supported_pkg_opt in supported_pkg_opts:
        if supported_pkg_opt in node.id:
            state.report(
                100, pkg.def_file, node,
                f'unexpected package configuration: {node.id}',
            )
            return
