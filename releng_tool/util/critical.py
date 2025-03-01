# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from typing import Any


def raise_for_critical(flag: Any = True) -> None:
    """
    raise for a critical exit state

    This call can be used to trigger a critical system exit state. This is
    for logic that have reached a failure state that should trigger the
    stop of the running process. When a provided value results in a
    conditional ``True`` state or no argument is provided, it is believed
    the process has triggered this "critical state" and this call will
    trigger the stop of the process.

    Args:
        flag (optional): the critical flag

    Raises:
        SystemExit: when a critical state is triggered
    """

    if flag:
        raise SystemExit(1)
