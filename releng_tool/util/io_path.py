# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from pathlib import Path
from releng_tool.util.string import expand
import os


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
