# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from copy import deepcopy


def replicate_package_attribs(opts, pkg):
    """
    replicate package attributes into an engine options entity

    Process a package entity (``RelengPackage``) and copies public attributes of
    the class into a provided options entity. This is to help expose internally
    tracked package options into internally managed engine stages (e.g. allowing
    the script build process to use all package options not defined in the API).

    Args:
        opts: the options to update
        pkg: the package entity with attributes to replicate
    """
    for key, value in pkg.__dict__.items():
        if not key.startswith('_'):
            opts.__dict__['_' + key] = deepcopy(value)
