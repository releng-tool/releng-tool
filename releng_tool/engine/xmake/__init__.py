# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

import platform
import sys


def detect_default_xmake_arch() -> str | None:
    """
    help detect an automatic architecture value for xmake

    It has been observed that some auto-detection logic for xmake-generated
    projects using mixed architectures for generic packages. For example,
    on Windows GitHub runners, auto-detection and use of clang would target
    x64, but try to link to x86 MSVC libraries.

    To workaround this, we can attempt to auto-detect architecture values to
    use before invoking `xmake config`. Then when configuring, we can force
    the architecture option `-a` to ensure consistency.

    This call should only be used for automatic architecture handling; but
    users should be able to override.

    Returns:
        the xmake-support architecture string or ``None``
    """

    plat = 'windows' if sys.platform == 'win32' else platform.system().lower()
    arch = platform.machine().lower()

    match (plat, arch):
        case ('windows', 'amd64' | 'x86_64'):
            return 'x64'
        case ('windows', 'arm64' | 'aarch64' | 'armv8'):
            return 'arm64'
        case ('windows', 'armv7' | 'arm'):
            return 'arm'
        case ('windows', _):
            return 'x86'
        case ('darwin', 'arm64' | 'aarch64'):
            return 'arm64'
        case ('darwin', _):
            return 'x86_64'
        case (_, 'arm64' | 'aarch64' | 'armv8'):
            return 'aarch64'
        case (_, 'armv7' | 'armv7l' | 'arm'):
            return 'armv7'

    return None
