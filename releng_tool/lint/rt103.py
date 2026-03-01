# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.lint import LintState
from releng_tool.packages import pkg_key
from releng_tool.packages.package import RelengPackage
import ast


def rt103(state: LintState, pkg: RelengPackage, nodes: list[ast.AST]):
    """
    perform linting "103" -- deprecated dependency configuration

    Args:
        state: the linting state
        pkg: the active package
        node: node being processed
    """

    deps_key = pkg_key(pkg.name, Rpk.DEPS)
    needs_key = pkg_key(pkg.name, Rpk.NEEDS)

    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == deps_key:
                state.report(
                    103, pkg.def_file, node,
                    'using deprecated dependency configuration',
                    extra=f"  (update '{deps_key}' to '{needs_key}')\n",
                )
                return
