# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from difflib import get_close_matches
from releng_tool.defs import GlobalAction
from releng_tool.defs import PkgAction
import os


def _populate_possible_pkgs(opts):
    """
    return the possible package names for this option set

    Will perform a simple query for possible package definitions expected for
    a releng-tool options set. Packages themselves are not verified "correct".

    Args:
        opts: the runtime options

    Returns:
        list of package names
    """

    possible_pkg_names = []

    for entry in os.listdir(opts.default_pkg_dir):
        pkg_dir = os.path.join(opts.default_pkg_dir, entry)
        if os.path.isdir(pkg_dir):
            possible_pkg_names.append(entry)

    return possible_pkg_names


def suggest(opts, value, pkg_finder=_populate_possible_pkgs):
    """
    determine target actions suggestions for a value that does not exist

    This call aims to provide a list of possible alternative suggestions a
    user could use if a given value does not match either an action, a
    package or a supported combination.

    Args:
        opts: the runtime options
        value: the value the user attempted
        pkg_finder (optional): call that determined what packages exist

    Returns:
        list of possible matches found, if any
    """

    # we have a valid package action; try to find matching packages
    if opts.pkg_action:
        possible_pkg_names = pkg_finder(opts)
        matches = get_close_matches(value, possible_pkg_names)
        if matches:
            matches2 = []
            for match in matches:
                matches2.append(f'{match}-{opts.pkg_action}')
            matches = matches2
    # no package action but we have a dash, check if there are any matches
    # to possible valid package actions
    elif '-' in value:
        part1, part2 = value.rsplit('-', 1)
        possible_pkg_names = pkg_finder(opts)

        # if the first part is a valid package, assume the package action
        # is incorrect and try to find a suggestion
        if part1 in possible_pkg_names:
            pkg_name = part1

            matches = get_close_matches(part2, PkgAction)
            if matches:
                matches2 = []
                for match in matches:
                    matches2.append(f'{pkg_name}-{match}')
                matches = matches2

        # if the package name is not valid, this is either an entire package
        # name that is incorrect, or a combination of both a bad package name
        # and a package action; only deal with the first case and try to
        # find a possible package
        else:
            matches = get_close_matches(value, possible_pkg_names)
            if not matches:
                matches = get_close_matches(part1, possible_pkg_names)
    # no possible package action; try to match a global action; if nothing
    # is found, try to match a package name
    else:
        matches = get_close_matches(value, GlobalAction)
        if not matches:
            possible_pkg_names = pkg_finder(opts)
            matches = get_close_matches(value, possible_pkg_names)

    if matches:
        matches.sort()

    return matches
