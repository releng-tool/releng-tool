# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.lint import LintState
from releng_tool.lint import lint_check
from releng_tool.packages import pkg_key
from releng_tool.packages.package import RelengPackage
from releng_tool.defs import PackageType
import ast


@lint_check(ver=[3, 1])
def rt116(state: LintState, pkg: RelengPackage, nodes: list[ast.AST]):
    """
    linting xmake-only configurations

    Args:
        state: the linting state
        pkg: the active package
        node: node being processed
    """

    # before checking for conditional ways the type would be set, perform
    # the simple check with the package instance
    if pkg.type == PackageType.XMAKE:
        return

    type_key = pkg_key(pkg.name, Rpk.TYPE)

    # first, ensure we have no scenario where xmake is the target type
    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == type_key:
                if isinstance(node.value, ast.Constant):
                    if node.value.value == PackageType.XMAKE:
                        return

    # confirmed no xmake type -- check for any type-specific configs
    msg = 'unexpected key for non-xmake package'
    key_checks = [
        pkg_key(pkg.name, Rpk.XMAKE_BUILD_TYPE),
        pkg_key(pkg.name, Rpk.XMAKE_NOINSTALL),
    ]

    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name):
                for key_check in key_checks:
                    if target.id == key_check:
                        state.report(
                            116, pkg.def_file, node,
                            f'{msg}: {key_check}',
                        )
                        break
