# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections.abc import Sequence
from queue import Queue
import re


def spdx_extract(raw):
    """
    extract license/exception strings from a spdx string

    The following accepts a SPDX license identifier and extracts license and
    exception identifiers into their own sets. These sets will be returned
    to a caller, as well as a flag to indicate if any known parsing issues
    were detected (e.g. a malformed identifier). Short licenses specifying
    the `+` hint will be minimized to just the short license.

    Note that this call does validate officially registered SPDX license or
    exception entries.

    Args:
        raw: the SPDX license identifier

    Returns:
        successful parsing, license set and exception set
    """

    valid = True
    licenses = set()
    exceptions = set()

    if raw:
        needs_license = False
        next_exception = False

        # break out expressions into parts
        raw = raw.replace('(', ' ').replace(')', ' ')
        parts = re.split(r'\s+(and|or|with|AND|OR|WITH)', raw)
        for part in parts:
            part = part.strip()
            if not part:
                continue

            # check if we need to process any operaters
            if part.lower() in ['and', 'or', 'with']:
                if needs_license or next_exception:
                    valid = False

                next_exception = part.lower() == 'with'
                needs_license = not next_exception
                continue

            if next_exception:
                exceptions.add(part)
                next_exception = False
            else:
                license_id = part.rstrip('+')
                licenses.add(license_id)
                needs_license = False

        if needs_license or next_exception:
            valid = False

    return valid, licenses, exceptions


def spdx_license_identifier(license_value):
    """
    determine if a license is a (custom) license identifier

    SPDX defines a license identifier field -- a locally unique identifier
    for licenses not found on the SPDX license list. These must be
    `LicenseRef-` prefixed strings followed by an identifier string containing
    only letters, numbers, a `.` or `-`.

    Args:
        license_value: the license value to check

    Returns:
        whether this is a license identifier
    """

    if not license_value:
        return False

    # custom license identifiers must start with `LicenseRef` (spdx)
    if not license_value.startswith('LicenseRef-'):
        return False

    id_str = license_value.removeprefix('LicenseRef-')
    return id_str.replace('.', '').replace('-', '').isalpha()


def spdx_parse(data):
    if not data:
        return None

    if isinstance(data, Sequence) and not isinstance(data, str):
        if isinstance(data, tuple):
            data = ') AND ('.join(data)
        else:
            data = ') OR ('.join(data)
        data = '(' + data + ')'

    q = Queue()
    s = []

    tokens = data.replace('(', ' ( ').replace(')', ' ) ').split()
    operators = ['AND', 'OR', 'WITH']

    # shunting yard algorithm for a postfix notation of license sets
    rejoin_license = False
    for token in tokens:
        if token == '(':
            s.append(token)
        elif token == ')':
            while True:
                if not s:
                    return None

                op = s.pop()
                if op == '(':
                    break

                q.put(op)

        elif token.upper() in operators:
            token = token.upper()
            if token == 'WITH':
                rejoin_license = True
                continue

            while s and s[-1] == 'AND' and token == 'OR':
                q.put(s.pop())
            s.append(token)
        elif rejoin_license:
            # if we split on a `WITH` operator, rebuild it for this token
            rejoin_license = False
            q.queue[-1] += ' WITH ' + token
        else:
            q.put(token)

        if rejoin_license:
            return None

    if rejoin_license:
        return None

    while s:
        op = s.pop()
        if op == '(':
            return None
        q.put(op)

    # build license sets
    MIN_STACK = 2
    while not q.empty():
        token = q.get()
        if token in operators:
            if len(s) < MIN_STACK:
                return None

            if token == 'AND':
                target = ConjunctiveLicenses()
            else:
                target = DisjunctiveLicenses()

            for node in reversed([s.pop(), s.pop()]):
                if type(node) is type(target):
                    target.extend(node)
                else:
                    target.append(node)

            s.append(target)
        else:
            s.append(token)

    # we should have a single license set/instance in the stack; return it
    return s.pop()


class LicenseEntries(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conjunctive = None

    def __str__(self):
        parts = []

        for entry in self:
            if isinstance(entry, LicenseEntries):
                parts.append('(' + str(entry) + ')')
            else:
                parts.append(entry)

        return self._str_operator().join(parts)

    def _str_operator(self):
        raise NotImplementedError


class ConjunctiveLicenses(LicenseEntries):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conjunctive = True

    def _str_operator(self):
        return ' AND '


class DisjunctiveLicenses(LicenseEntries):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conjunctive = False

    def _str_operator(self):
        return ' OR '
