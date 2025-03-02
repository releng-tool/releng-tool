# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from pathlib import Path
from releng_tool.util.critical import raise_for_critical
from releng_tool.util.log import err
import os


def mkdir(dir_: str | bytes | os.PathLike, *args: str | bytes | os.PathLike,
        **kwargs) -> None | Path:
    """
    ensure the provided directory exists

    .. versionadded:: 0.3
    .. versionchanged:: 0.13 Add support for ``critical``.
    .. versionchanged:: 1.3 Accepts multiple paths components.
    .. versionchanged:: 1.3 Returns the created path.
    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.

    Attempts to create the provided directory. If the directory already exists,
    this method has no effect. If the directory does not exist and could not be
    created, this method will return ``None``. Also, if an error has been
    detected, an error message will be output to standard error (unless
    ``quiet`` is set to ``True``).

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        if releng_mkdir('my-directory'):
            print('directory was created')
        else:
            print('directory was not created')

        target_dir = releng_mkdir(TARGET_DIR, 'sub-folder')
        if target_dir:
            # output] target directory: <target>/sub-folder
            print('target directory:', target_dir)
        else:
            print('directory was not created')

    Args:
        dir_: the directory
        *args (optional): additional components of the directory
        **quiet (optional): whether or not to suppress output (defaults
            to ``False``)
        **critical (optional): whether or not to stop execution on
            failure (defaults to ``False``)

    Returns:
        the directory that exists; ``None`` if the directory could not
        be created
    """
    quiet = kwargs.get('quiet')
    critical = kwargs.get('critical')

    final_dir = Path(os.fsdecode(dir_), *map(os.fsdecode, args))
    try:
        final_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        if not quiet:
            err('unable to create directory: {}\n'
                '    {}', final_dir, e)
        raise_for_critical(critical)
        return None

    return final_dir
