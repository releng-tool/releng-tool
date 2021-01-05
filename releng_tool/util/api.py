# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from copy import deepcopy
from releng_tool.defs import PackageInstallType

def package_install_type_to_api_type(install_type):
    """
    convert an internal package-install-type to an api-compatible string

    Both the configuration and installation stages provide a package
    installation type to allow the stage to decide where the installation phase
    will place assets. The internal package-install-type (an enumeration) is not
    managed in the API world -- the interface expects fixed string values. This
    helper method provides said conversion.

    Args:
        install_type: the package installation type

    Returns:
        the package installation type in string format
    """
    if install_type == PackageInstallType.HOST:
        return 'host'
    elif install_type == PackageInstallType.IMAGES:
        return 'images'
    elif install_type == PackageInstallType.STAGING:
        return 'staging'
    elif install_type == PackageInstallType.STAGING_AND_TARGET:
        return 'staging_and_target'
    elif install_type == PackageInstallType.TARGET:
        return 'target'
    else:
        return 'unknown'

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
