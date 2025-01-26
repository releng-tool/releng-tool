# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

import os


# environment variables used to hint if a ci runner is in a debugging run
RUNNER_DEBUG_HINTS = [
    'ACTIONS_RUNNER_DEBUG',  # github
    'CI_DEBUG_TRACE',  # gitlab
    'RUNNER_DEBUG',  # github (legacy)
]


def detect_ci_runner_debug_mode():
    """
    attempt to detect a ci runner in a debugging mode

    When running a releng-tool job in a CI runner, there are scenarios when
    a CI job may be running in a "debug" mode (triggered by a user to help
    debug a possible failure by re-running with more logs). This call is
    used to help detect such a scenario, which releng-tool may use to
    automatically enable information for a user.

    Returns:
        whether a ci debugging mode is detected
    """
    return any(x in os.environ for x in RUNNER_DEBUG_HINTS)
