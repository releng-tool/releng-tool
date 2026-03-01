# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.lint import LintState
from releng_tool.packages import pkg_key
from releng_tool.packages.package import RelengPackage
import ast


def rt115(state: LintState, pkg: RelengPackage, nodes: list[ast.AST]):
    """
    linting planned removal of remote-configuration/scripts

    Args:
        state: the linting state
        pkg: the active package
        node: node being processed
    """

    msg = 'remote features are planned to be removed'
    key_checks = [
        pkg_key(pkg.name, Rpk.REMOTE_CONFIG),
        pkg_key(pkg.name, Rpk.REMOTE_SCRIPTS),
    ]

    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name):
                for key_check in key_checks:
                    if target.id == key_check:
                        state.report(
                            115, pkg.def_file, node,
                            f'{msg}: {key_check}',
                        )
                        break
