# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.lint import LintState
from releng_tool.packages import pkg_key
from releng_tool.packages.package import RelengPackage
from releng_tool.defs import PackageType
import ast


def rt108(state: LintState, pkg: RelengPackage, nodes: list[ast.AST]):
    """
    linting make-only configurations

    Args:
        state: the linting state
        pkg: the active package
        node: node being processed
    """

    # before checking for conditional ways the type would be set, perform
    # the simple check with the package instance
    if pkg.type == PackageType.MAKE:
        return

    type_key = pkg_key(pkg.name, Rpk.TYPE)

    # first, ensure we have no scenario where make is the target type
    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == type_key:
                if isinstance(node.value, ast.Constant):
                    if node.value.value == PackageType.MAKE:
                        return

    # confirmed no make type -- check for any type-specific configs
    msg = 'unexpected key for non-make package'
    key_checks = [
        pkg_key(pkg.name, Rpk.MAKE_NOINSTALL),
    ]

    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name):
                for key_check in key_checks:
                    if target.id == key_check:
                        state.report(
                            108, pkg.def_file, node,
                            f'{msg}: {key_check}',
                        )
                        break
