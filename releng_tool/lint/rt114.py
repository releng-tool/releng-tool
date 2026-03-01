# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.lint import LintState
from releng_tool.packages import pkg_key
from releng_tool.packages.package import RelengPackage
import ast


def rt114(state: LintState, pkg: RelengPackage, nodes: list[ast.AST]):
    """
    linting devmode-only configurations

    Args:
        state: the linting state
        pkg: the active package
        node: node being processed
    """

    devmode_rev_key = pkg_key(pkg.name, Rpk.DEVMODE_REVISION)

    # first, ensure we have no scenario where development mode revision is set
    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == devmode_rev_key:
                return

    # confirmed no devmode revisions -- check for any type-specific configs
    msg = 'attempt to tailor devmode option for a non-devmode package'
    key_checks = [
        pkg_key(pkg.name, Rpk.DEVMODE_IGNORE_CACHE),
        pkg_key(pkg.name, Rpk.DEVMODE_PATCHES),
        pkg_key(pkg.name, Rpk.DEVMODE_SKIP_INTEGRITY_CHECK),
        pkg_key(pkg.name, Rpk.ONLY_DEVMODE),
    ]

    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name):
                for key_check in key_checks:
                    if target.id == key_check:
                        state.report(
                            114, pkg.def_file, node,
                            f'{msg}: {key_check}',
                        )
                        break
