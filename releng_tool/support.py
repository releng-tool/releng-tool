# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
from releng_tool import __version__ as releng_version
from releng_tool.util.critical import raise_for_critical
from releng_tool.util.env import env_wrap
from releng_tool.util.log import err
from releng_tool.util.path import P
from runpy import run_path
import inspect
import os


def releng_include(file_path: str | bytes | os.PathLike) -> None:
    """
    include/execute a script

    .. versionadded:: 0.12
    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.

    The provided call will execute code at the provided file path. The path
    will be relative to the caller's script, unless an absolute path is
    provided. The executed script will be initialized with globals matching
    the caller's script.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        # load "my-other-script" found alongside the current script
        releng_include('my-other-script')

    Args:
        file_path: the script to invoke
    """

    caller_stack = inspect.stack()[1]

    final_file = Path(os.fsdecode(file_path))

    if final_file.is_absolute():
        target_script = final_file
    else:
        invoked_script = caller_stack[1]
        invoked_script_base = Path(invoked_script).parent
        target_script = invoked_script_base / final_file

    ctx_globals = caller_stack[0].f_globals

    with releng_script_envs(str(target_script), ctx_globals) as script_env:
        run_path(str(target_script), init_globals=script_env)


@contextmanager
def releng_script_envs(script, ctxenv):
    script_dir = os.path.dirname(script)
    script_env = ctxenv.copy()

    # when invoking an include script, we will override the script
    # environment hints based on the path of the included script; but
    # restore back to the original variables once completed
    restore_keys = [
        'RELENG_SCRIPT',
        'RELENG_SCRIPT_DIR',
    ]

    saved_env = {}
    for key in restore_keys:
        saved_env[key] = os.environ.get(key, None)

    try:
        for env in (env_wrap(), script_env):
            env['RELENG_SCRIPT'] = P(script)
            env['RELENG_SCRIPT_DIR'] = P(script_dir)

        yield script_env
    finally:
        # restore any overrides that may have been set
        for k, v in saved_env.items():
            if v is not None:
                os.environ[k] = v
            else:
                os.environ.pop(k, None)


def require_version(minver=None, **kwargs):
    """
    perform a required-version check

    .. versionadded:: 0.11
    .. versionchanged:: 2.0 Support maximum version.

    Enables a caller to explicitly check for a required releng-tool version.
    Invoking this function with a dotted-separated ``version`` string, the
    string will be parsed and compared with the running releng-tool version.
    If the required version is met, this method will have no effect. In the
    event that the required version is not met, the exception ``SystemExit``
    will be raised if the critical flag is set; otherwise this call will
    return ``False``.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        # ensure we are using releng-tool v1
        releng_require_version('1.0.0')

    Args:
        minver: dotted-separated minimum version string
        **quiet (optional): whether or not to suppress output
        **critical (optional): whether or not to stop execution on failure
        **maxver (optional): dotted-separated maximum version string

    Returns:
        ``True`` if the version check is met; ``False`` if the version check
        has failed

    Raises:
        SystemExit: if the version check fails with ``critical=True``
    """
    critical = kwargs.get('critical', True)
    maxver = kwargs.get('maxver')
    quiet = kwargs.get('quiet')

    rv = True

    if minver:
        requested = minver.split('.')
        current = releng_version.split('.')
        rv = requested <= current
        if not rv:
            if not quiet:
                args = {
                    'detected': releng_version,
                    'required': minver,
                }
                err('''
required releng-tool version check has failed

This project has indicated a required minimum version of releng-tool to
be installed on this system; however, an older version has been
detected:

    (required) {required}
    (detected) {detected}

Please update to a more recent version:

 https://docs.releng.io/install/
'''.strip().format(**args))

            raise_for_critical(critical)

    if maxver:
        requested = maxver.split('.')
        current = releng_version.split('.')
        rv = requested >= current
        if not rv:
            if not quiet:
                args = {
                    'detected': releng_version,
                    'required': maxver,
                }
                err('''
required releng-tool version check has failed

This project has indicated a required maximum version of releng-tool to
be installed on this system; however, an older version has been
detected:

    (required) {required}
    (detected) {detected}

This package needs to upgraded or releng-tool needs to be downgraded.
'''.strip().format(**args))

            raise_for_critical(critical)

    return rv
