# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from pathlib import PosixPath
from pathlib import WindowsPath
import os
import sys


# python v3.12+ introduces support for using Path as a base class
if sys.version_info >= (3, 12):
    _PathBase = Path
elif os.name == 'nt':
    _PathBase = WindowsPath
else:
    _PathBase = PosixPath


class P(_PathBase):
    """
    relaxed path instance

    Provides a path helper that provides the capabilities of pathlib's `Path`,
    but includes str-like capabilities. This includes support for the `+`
    operator as well as equality check.

    This class aims to address two things. First, to improve the ability
    for implementations to transition from str paths to pathlib types.
    Second, the convenience of support the `+` operator when handling
    scenarios such as system prefix appending.

    This helper is only aimed to be used for Path-like instances shared
    in script helpers.
    """

    def __add__(self, other: str) -> str:
        return f'{self.__str__()}{other}'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            other = Path(other)

        return super().__eq__(other)

    def __hash__(self) -> int:
        return super().__hash__()

    def __radd__(self, other: str) -> str:
        return f'{other}{self.__str__()}'
