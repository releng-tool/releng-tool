# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.defs import VcsType
from releng_tool.lint import LintState
from releng_tool.packages import pkg_key
from releng_tool.packages.package import RelengPackage
import ast


def rt102(state: LintState, pkg: RelengPackage, nodes: list[ast.AST]):
    """
    perform linting "102" -- explicit url vcs-type with files

    Args:
        state: the linting state
        pkg: the active package
        node: node being processed
    """

    pkg_site_value: str | None = None
    pkg_vcs_type_node: ast.Assign | None = None
    pkg_vcs_type_value: str | None = None

    site_key = pkg_key(pkg.name, Rpk.SITE)
    vcs_type_key = pkg_key(pkg.name, Rpk.VCS_TYPE)

    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == site_key:
                if isinstance(node.value, ast.Constant):
                    pkg_site_value = str(node.value.value)
                    break

            if isinstance(target, ast.Name) and target.id == vcs_type_key:
                if isinstance(node.value, ast.Constant):
                    pkg_vcs_type_node = node
                    pkg_vcs_type_value = str(node.value.value)
                    break

        if pkg_site_value and pkg_vcs_type_node:
            break

    # we need both the site and vcs-type for this check
    if not pkg_site_value or not pkg_vcs_type_node:
        return

    # ignore if no explicit vcs type set
    if pkg_vcs_type_value != VcsType.URL:
        return

    # verify if package is using a file path for a url vcs type
    if pkg_site_value.startswith('file://'):
        state.report(
            102, pkg.def_file, pkg_vcs_type_node,
            f'explicit url vcs-type with files is deprecated: {vcs_type_key}',
            extra=f"  (update '{vcs_type_key}' to 'file')\n",
        )
