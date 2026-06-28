# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolReleaseCheckError
from releng_tool.util.log import debug
from releng_tool.util.log import verbose
from releng_tool.util.log import warn


def release_mode_check(engine, pkgs):
    """
    perform a release mode check

    A user can invoke releng-tool with a `--release` argument to help ensure
    a given build is not being performed using features like development mode.
    This aims to be a sanity check to help catch undesired runtime states.

    Args:
        engine: the engine
        pkgs: the project's packages

    Raises:
        RelengToolReleaseCheckError: raised if a release check issue is found
    """

    # ignore if not running in a release mode
    if not engine.opts.release:
        return

    debug('release mode check being performed')
    issues: list[str] = []

    # ensure we are not running in a development mode
    if engine.opts.devmode:
        issues.append('detected development mode')

    # ensure we are not running in a local-sources mode
    if engine.opts.local_srcs:
        issues.append('detected local-sources mode')

    # ensure a user has not provided a global action
    if engine.opts.gbl_action:
        issues.append(f'action detected: {engine.opts.gbl_action}')

    # ensure a user has not provided a target-specific action
    if engine.opts.target_action:
        suffix = f'-{engine.opts.pkg_action}' if engine.opts.pkg_action else ''
        issues.append(f'action detected: {engine.opts.target_action}{suffix}')

    for pkg in pkgs:
        # ensure we are not using a force revision; should be using a
        # package's revision defined in the project
        if pkg.revision_forced:
            issues.append(f'{pkg.name}: detected a forced revision')

    # any detected issues? throw a release check error
    if issues:
        ignore_check = 'releng.ignore_release_check' in engine.opts.quirks
        log_method = warn if ignore_check else verbose

        result = '\n  - '.join(issues)
        log_method(f'''\
release check failure but user as opt to ignore this
  - {result}
'''.strip())

        if not ignore_check:
            raise RelengToolReleaseCheckError(issues)
