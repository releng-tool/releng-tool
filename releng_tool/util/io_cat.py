# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from itertools import chain
from pathlib import Path
from shutil import copyfileobj
import os
import sys


def cat(file: str | bytes | os.PathLike,
        *args: str | bytes | os.PathLike) -> bool:
    """
    concatenate files and print on the standard output

    .. versionadded:: 0.11
    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.

    Attempts to read one or more files provided to this call. For each file, it
    will be read and printed out to the standard output.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        releng_cat('my-file')

    Args:
        file: the file
        *args (optional): additional files to include

    Returns:
        ``True`` if all the files exists and were printed to the standard
        output; ``False`` if one or more files could not be read
    """

    files = []

    for f in chain([file], args):
        fentry = Path(os.fsdecode(f))

        if not fentry.is_file():
            return False

        files.append(fentry)

    try:
        for fentry in files:
            with fentry.open(encoding='utf-8') as fp:
                copyfileobj(fp, sys.stdout)
    except OSError:
        return False
    else:
        return True
