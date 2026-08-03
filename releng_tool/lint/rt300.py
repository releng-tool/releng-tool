# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.lint import LintState
from releng_tool.lint import lint_check
import ast


@lint_check(ver=[4, 2])
def rt300(state: LintState, path: Path, nodes: list[ast.AST]):
    """
    linting project configuration for deprecated releng_register_path call

    Args:
        state: the linting state
        path: the engine options
        nodes: nodes being processed
    """

    for node in nodes:
        if isinstance(node, ast.Name) and node.id == 'releng_register_path':
            state.report(
                300, path, node,
                'use of deprecated `releng_register_path`; '
                'switch to `releng_register_python_path`',
            )
