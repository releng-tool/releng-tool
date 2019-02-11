#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ..api import RelengInstallOptions
from ..defs import *
from ..util.api import packageInstallTypeToApiType
from ..util.api import replicatePackageAttribs
from ..util.io import interimWorkingDirectory
from ..util.log import *
from .autotools.install import install as installAutotools
from .cmake.install import install as installCmake
from .python.install import install as installPython
from .script.install import install as installScript
import sys

def stage(engine, pkg, script_env):
    """
    handles the installation stage for a package

    With a provided engine and package instance, the installation stage will be
    processed.

    Args:
        engine: the engine
        pkg: the package being built
        script_env: script environment information

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    note('installing {}...'.format(pkg.name))
    sys.stdout.flush()

    if pkg.build_subdir:
        build_dir = pkg.build_subdir
    else:
        build_dir = pkg.build_dir

    if pkg.install_type == PackageInstallType.HOST:
        dest_dirs = [engine.opts.host_dir]
    elif pkg.install_type == PackageInstallType.IMAGES:
        dest_dirs = [engine.opts.images_dir]
    elif pkg.install_type == PackageInstallType.STAGING:
        dest_dirs = [engine.opts.staging_dir]
    elif pkg.install_type == PackageInstallType.STAGING_AND_TARGET:
        dest_dirs = [engine.opts.staging_dir, engine.opts.target_dir]
    else:
        # default to target directory
        dest_dirs = [engine.opts.target_dir]

    install_opts = RelengInstallOptions()
    replicatePackageAttribs(install_opts, pkg)
    install_opts.build_dir = build_dir
    install_opts.build_output_dir = pkg.build_output_dir
    install_opts.cache_file = pkg.cache_file
    install_opts.def_dir = pkg.def_dir
    install_opts.dest_dirs = dest_dirs
    install_opts.env = script_env
    install_opts.ext = pkg.ext_modifiers
    install_opts.host_dir = engine.opts.host_dir
    install_opts.images_dir = engine.opts.images_dir
    install_opts.install_type = packageInstallTypeToApiType(pkg.install_type)
    install_opts.name = pkg.name
    install_opts.prefix = pkg.prefix
    install_opts.staging_dir = engine.opts.staging_dir
    install_opts.target_dir = engine.opts.target_dir
    install_opts.version = pkg.version

    installer = None
    if pkg.type in engine.registry.package_types:
        def _(opts):
            return engine.registry.package_types[pkg.type].install(
                pkg.type, opts)
        installer = _
    elif pkg.type == PackageType.AUTOTOOLS:
        installer = installAutotools
    elif pkg.type == PackageType.CMAKE:
        installer = installCmake
    elif pkg.type == PackageType.PYTHON:
        installer = installPython
    elif pkg.type == PackageType.SCRIPT:
        installer = installScript

    if not installer:
        err('installer type is not implemented: {}'.format(pkg.type))
        return False

    with interimWorkingDirectory(build_dir):
        installed = installer(install_opts)
        if not installed:
            return False

    return True
