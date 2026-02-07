# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from pathlib import Path
from releng_tool.util.critical import raise_for_critical
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.string import expand
import os
import sys


def path_input(path: str | bytes | os.PathLike) -> Path:
    """
    decoded and expand a raw path into an path object

    This call helps take a path value on various types and generates a Path
    object. The argument is decoded (``os.fsdecode``). The decoded path is
    expanded on for any variables that may be provided. The resulting path is
    prepared in a ``Path`` entity.

    Args:
        path: the path

    Returns:
        the decoded expanded path as a Path object
    """

    return Path(expand(os.fsdecode(path)))


def releng_register_path(dir_: str | bytes | os.PathLike,
        *, critical: bool = True):
    """
    register a provided directory into the module search path

    .. versionadded:: 2.7

    This call will register a provided path into the Python module search path
    (``sys.path``). This can be useful for situations when trying to load a
    local/relative folder containing extensions or other enhancements a
    developer wants to use/import. If ``critical`` is set to ``True`` and the
    specified directory could not be registered for any reason, this call will
    issue a system exit (``SystemExit``).

    If the provided path is already registered, the call is ignored and will
    return as if a registration was made (``True``).

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        releng_register_path(ROOT_DIR.parent / 'my-other-folder')

    Args:
        dir_: the directory to register
        critical (optional): whether or not to stop execution on failure

    Returns:
        ``True`` if the path has been registered; ``False`` if the registration
        has failed

    Raises:
        SystemExit: if the registration fails with ``critical=True``
    """
    success = False

    path = path_input(dir_)
    if path.is_dir():
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.append(path_str)
            debug(f'registered module search path: {path}')
        success = True
    else:
        err('unable to register missing directory into module search path\n'
            f'    {path}')

    raise_for_critical(not success and critical)
    return success
