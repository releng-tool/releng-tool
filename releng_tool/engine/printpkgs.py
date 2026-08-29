# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.apimode import API_STATE
from releng_tool.packages.package import RelengPackage
from releng_tool.util.log import log


def printpkgs(pkgs: list[RelengPackage]):
    """
    request to print project names to the output stream

    Provides a development helper to print package names to the output
    stream. This can be used to help determine which packages are
    configured for a run.

    Args:
        pkgs: the package to print
    """

    for pkg in sorted(pkgs, key=lambda pkg: pkg.name):
        suffix = f' ({pkg.revision})' if pkg.revision else ''
        log(f'{pkg.name}{suffix}')

        api_data = API_STATE['printpkgs'][pkg.name].fetch()
        pkg.populate_api(base=api_data)
