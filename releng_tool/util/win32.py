# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

import ctypes
import os
import re
import subprocess

try:
    import ctypes.wintypes

    try:
        import winreg as reg
    except ImportError:
        import _winreg as reg
except Exception:  # noqa: S110
    pass


def enable_ansi():
    """
    enable ansi in a windows command window

    Adjusts a Windows command window to support parsing control characters
    pushed to output handle. The primary goal is to support color control
    characters generated by releng-tool's logging events.
    """

    kern32 = ctypes.windll.kernel32

    # fetch the current console mode
    mode = ctypes.wintypes.DWORD()
    handle = kern32.GetStdHandle(subprocess.STD_OUTPUT_HANDLE)
    kern32.GetConsoleMode(handle, ctypes.byref(mode))

    # adjust the console mode to parse output in the console
    # https://docs.microsoft.com/en-us/windows/console/setconsolemode
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 7
    mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
    kern32.SetConsoleMode(handle, mode)


def find_win32_python_interpreter(target):
    """
    find a python interpreter on a windows system

    Attempts to find the full path of a Python interpreter on a Windows system
    by checking the running context's registry. This call will cycle through
    various registry hives and match an installed interpreter based off the
    provided target string. For example, providing a ``target`` value of
    ``python3.9`` (or ``3.9``) will attempt to find the first available Python
    3.9 interpreter on the system. When providing a non-specific Python version
    (e.g. ``python3``), the most recent version of the interpreter type will be
    used). User-installed interpreters are promoted over shared interpreters.

    Args:
        target: the target interpreter

    Returns:
        the interpreter path; ``None`` if no interpreter could be found
    """

    if not target:
        return None

    PYTHON_PREFIX = 'python'
    PYTHON_CORE = r'Software\Python\PythonCore'
    INSTALL_PATH_KEY = r'\InstallPath'
    PYTHON_EXEC = r'python.exe'

    # remove any python prefix ('python3.8' -> '3.8')
    if target.startswith(PYTHON_PREFIX):
        target = target[len(PYTHON_PREFIX):]

    # keep track of a dictionary of available interpreters when trying to pick
    # a provided major version (e.g. "python3"), when cycling through all the
    # available registry hives
    found_interpreters = {}

    # see also https://www.python.org/dev/peps/pep-0514/
    for hive, key, flags in [
        (reg.HKEY_CURRENT_USER, PYTHON_CORE, 0),
        (reg.HKEY_LOCAL_MACHINE, PYTHON_CORE, reg.KEY_WOW64_64KEY),
        (reg.HKEY_LOCAL_MACHINE, PYTHON_CORE, reg.KEY_WOW64_32KEY),
    ]:
        try:
            # search for official python releases
            with reg.OpenKeyEx(hive, key, 0, reg.KEY_READ | flags) as root:
                # compile a list of known version
                i = 0
                installed_vers = []
                raw_interpreters = {}
                while True:
                    try:
                        raw_interpreter = reg.EnumKey(root, i)

                        # remove any architecture that may be registered for
                        # the detected interpreter; e.g. "python37-32"
                        interpreter = raw_interpreter.split('-', 1)[0]
                        raw_interpreters[interpreter] = raw_interpreter

                        installed_vers.append(interpreter)
                    except OSError:
                        break
                    i += 1
                if not installed_vers:
                    continue

                # sort by newest interpreter
                _sort_interpreters(installed_vers)

                # find a version which matches are desired target
                target_ver = None
                if target in installed_vers:
                    target_ver = target
                # first available version?
                elif not target:
                    target_ver = installed_vers[0]
                # if we do have an explicit match and only a major version is
                # provided, attempt to find a first available (most recent)
                # interpreter available on the system
                elif '.' not in target:
                    target_major = target + '.'

                    if any(v.startswith(target_major) for v in installed_vers):
                        for installed_ver in installed_vers:
                            if installed_ver.startswith(target_major):
                                target_ver = installed_ver
                                break

                # skip root if target version cannot be found
                if not target_ver:
                    continue

                # skip version if already found in another hive
                if target_ver in found_interpreters:
                    continue

                # load key to find the interpreter's path
                base_key = raw_interpreters[target_ver]
                try:
                    with reg.OpenKey(root, base_key + INSTALL_PATH_KEY) as k:
                        try:
                            install_path = reg.QueryValue(k, '')
                            full_path = os.path.join(install_path, PYTHON_EXEC)

                            # rule out the registry item if the path/executable
                            # does not exists
                            if not os.path.exists(full_path):
                                continue

                            # if matched to a target, stop
                            if target and target_ver == target:
                                return full_path

                            found_interpreters[target_ver] = full_path
                            continue
                        except ImportError:
                            pass
                except OSError:
                    pass
        except OSError:
            pass

    # sort by newest interpreter
    if found_interpreters:
        installed_vers = list(found_interpreters.keys())
        _sort_interpreters(installed_vers)
        return found_interpreters[installed_vers[0]]

    return None


def _sort_interpreters(o):
    """
    in-place sort a list of interpreters

    A helper method (to be used with ``find_interpreter``) to help sort a list
    of interpreters by comparing and prioritizing detected version strings.
    Newer interpreters will be sorted before older interpreters.

    Args:
        o: the list to sort
    """

    o.sort(
        key=lambda f: [int(x) for x in re.sub(r'[^\d\.]', '', f).split('.')],
        reverse=True)
