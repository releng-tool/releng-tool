# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.lint import LintState
from releng_tool.packages import pkg_key
from releng_tool.packages.package import RelengPackage
from releng_tool.defs import PackageInstallType
import ast


def rt104(state: LintState, pkg: RelengPackage, nodes: list[ast.AST]):
    """
    perform linting "104" -- host provides with non-host package

    Args:
        state: the linting state
        pkg: the active package
        node: node being processed
    """

    found_non_host_install_type: bool | None = None
    host_provides_node: ast.Assign | None = None

    host_provides_key = pkg_key(pkg.name, Rpk.HOST_PROVIDES)
    install_type_key = pkg_key(pkg.name, Rpk.INSTALL_TYPE)

    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            # grab any host-provides entry
            if isinstance(target, ast.Name) and target.id == host_provides_key:
                host_provides_node = node
                break

            # skip if we already found a non-host install type registration
            if found_non_host_install_type is True:
                continue

            # grab the first install type not targeting a host setup
            if isinstance(target, ast.Name) and target.id == install_type_key:
                if isinstance(node.value, ast.Constant):
                    if node.value.value == PackageInstallType.HOST:
                        found_non_host_install_type = False
                    else:
                        found_non_host_install_type = True
                    break

        if host_provides_node and found_non_host_install_type:
            break

    # we need both the host-provides node and install-type for this check
    if not host_provides_node or found_non_host_install_type is False:
        return

    state.report(
        104, pkg.def_file, host_provides_node,
        'non-host package providing host package',
        extra=f'''\
  (remove '{host_provides_key}'?)
  (set '{install_type_key}' to 'host'?)
''',
    )
