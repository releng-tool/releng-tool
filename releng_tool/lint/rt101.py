# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.lint import LintState
from releng_tool.opts import RelengEngineOptions
from releng_tool.packages import pkg_key
from releng_tool.packages.package import RelengPackage
from releng_tool.util.spdx import spdx_extract
from releng_tool.util.spdx import spdx_license_identifier
import ast


def rt101(state: LintState, opts: RelengEngineOptions,
        pkg: RelengPackage, node: ast.AST):
    """
    perform linting "101" -- unexpected spdx license text

    Args:
        state: the linting state
        opts: runtime options
        pkg: the active package
        node: node being processed
    """

    # find a package's license configuration key (left) assignment
    if not isinstance(node, ast.Name) or not isinstance(node.ctx, ast.Store) \
            or node.id != pkg_key(pkg.name, Rpk.LICENSE):
        return

    detectedSpdxIssues = []

    for license_entry in pkg.license:
        parsed, licenses, exceptions = spdx_extract(license_entry)

        for nested_license in licenses:
            if spdx_license_identifier(nested_license):
                continue

            entry = opts.spdx['licenses'].get(nested_license, None)
            if entry:
                if entry['deprecated']:
                    detectedSpdxIssues.append(
                        F'deprecated spdx license detected: {nested_license}')
            else:
                detectedSpdxIssues.append(
                    f'unknown spdx license detected: {nested_license}')

        for exception in exceptions:
            entry = opts.spdx['exceptions'].get(exception, None)
            if entry:
                if entry['deprecated']:
                    detectedSpdxIssues.append(
                        'deprecated spdx license exception '
                       f'detected: {exception}')
            else:
                detectedSpdxIssues.append(
                    F'unknown spdx license exception detected {exception}')

        if not parsed:
            detectedSpdxIssues.append('unexpected spdx license format detected')

    if detectedSpdxIssues:
        state.report(
            101, pkg.def_file, node,
            f'unexpected spdx license configuration: {node.id}',
            extra='  - ' + '\n  - '.join(detectedSpdxIssues) + '\n',
        )
