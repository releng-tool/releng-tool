# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

from ..api import RelengConfigureOptions
from ..defs import *
from ..util.api import packageInstallTypeToApiType
from ..util.api import replicatePackageAttribs
from ..util.io import interimWorkingDirectory
from ..util.log import *
from .autotools.configure import configure as configureAutotools
from .cmake.configure import configure as configureCmake
from .script.configure import configure as configureScript
import sys

def stage(engine, pkg, script_env):
    """
    handles the configuration stage for a package

    With a provided engine and package instance, the configuration stage will be
    processed.

    Args:
        engine: the engine
        pkg: the package being configured
        script_env: script environment information

    Returns:
        ``True`` if the configuration stage is completed; ``False`` otherwise
    """

    note('configuring {}...'.format(pkg.name))
    sys.stdout.flush()

    # ignore configuration step for types which do not have one
    if pkg.type == PackageType.PYTHON:
        return True

    if pkg.build_subdir:
        build_dir = pkg.build_subdir
    else:
        build_dir = pkg.build_dir

    configure_opts = RelengConfigureOptions()
    replicatePackageAttribs(configure_opts, pkg)
    configure_opts.build_dir = build_dir
    configure_opts.build_output_dir = pkg.build_output_dir
    configure_opts.conf_defs = pkg.conf_defs
    configure_opts.conf_env = pkg.conf_env
    configure_opts.conf_opts = pkg.conf_opts
    configure_opts.def_dir = pkg.def_dir
    configure_opts.env = script_env
    configure_opts.ext = pkg.ext_modifiers
    configure_opts.host_dir = engine.opts.host_dir
    configure_opts.install_type = packageInstallTypeToApiType(pkg.install_type)
    configure_opts.name = pkg.name
    configure_opts.prefix = pkg.prefix
    configure_opts.staging_dir = engine.opts.staging_dir
    configure_opts.symbols_dir = engine.opts.symbols_dir
    configure_opts.target_dir = engine.opts.target_dir
    configure_opts.version = pkg.version
    configure_opts._quirks = engine.opts.quirks

    # if package has a job-override value, use it over any global option
    if pkg.fixed_jobs:
        configure_opts.jobs = pkg.fixed_jobs
        configure_opts.jobsconf = pkg.fixed_jobs
    else:
        configure_opts.jobs = engine.opts.jobs
        configure_opts.jobsconf = engine.opts.jobsconf

    configurer = None
    if pkg.type in engine.registry.package_types:
        def _(opts):
            return engine.registry.package_types[pkg.type].configure(
                pkg.type, opts)
        configurer = _
    elif pkg.type == PackageType.AUTOTOOLS:
        configurer = configureAutotools
    elif pkg.type == PackageType.CMAKE:
        configurer = configureCmake
    elif pkg.type == PackageType.SCRIPT:
        configurer = configureScript

    if not configurer:
        err('configurer type is not implemented: {}'.format(pkg.type))
        return False

    with interimWorkingDirectory(build_dir):
        configured = configurer(configure_opts)
        if not configured:
            return False

    return True
