# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.lint import LintState
from releng_tool.lint import lint_check
from releng_tool.opts import RelengEngineOptions
from releng_tool.defs import ConfKey
import ast


@lint_check(ver=[3, 2])
def rt200(state: LintState, opts: RelengEngineOptions, nodes: list[ast.AST]):
    """
    linting project configuration for use of releng_config and global options

    Args:
        state: the linting state
        opts: the engine options
        nodes: nodes being processed
    """

    releng_config_exists = False

    for node in nodes:
        if isinstance(node, ast.Name) and node.id == 'releng_config':
            releng_config_exists = True
            break

    if not releng_config_exists:
        return

    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id in ConfKey:
                    state.report(
                        200, opts.conf_point, node,
                        'use of global option is ignored when using '
                       f'releng_config: {target.id}',
                    )
