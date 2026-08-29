# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.opts import RelengEngineOptions
from releng_tool.packages.package import RelengPackage
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.log import verbose
import time


# duration to wait after displaying versions at the start of a run
DEFAULT_DELAY_START_SECONDS = 10


def package_versions_banner(
        opts: RelengEngineOptions, pkgs: list[RelengPackage]):
    """
    request to print package versions to the output stream

    This call will help print known package revisions during the start of a
    releng-tool run. This is primarily to help with logging inspection for
    runs such as CI, where developers can inspect what revisions are going to
    or have be used (without having to check content such as SBOMs).

    Args:
        opts: options used to configure the engine
        pkgs: the packages to be processed
    """

    # ignore for any explicit action run
    if opts.gbl_action or opts.pkg_action or opts.target_action:
        return

    # ignore banner if project opts out of printing this information
    if 'releng.log.skip_package_versions_banner' in opts.quirks:
        return

    note('package version configuration')
    for pkg in sorted(pkgs, key=lambda pkg: pkg.name):
        # if we have revision, use it in the print
        if pkg.revision:
            log(f'{pkg.name}: {pkg.revision}')
        # although, not all packages may have a revision (e.g. site-only fetch);
        # if we have a site, try printing it instead
        elif pkg.site:
            log(f'{pkg.name}: {pkg.site}')

    # if a user requests to wait a moment after dumping the revision
    # information, hold
    if opts.delay_start:
        verbose('delaying start for a moment (per user request)...')
        time.sleep(DEFAULT_DELAY_START_SECONDS)
