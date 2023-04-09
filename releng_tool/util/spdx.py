# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

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
        parts = raw.replace('(', ' ').replace(')', ' ').split()
        for part in parts:
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
