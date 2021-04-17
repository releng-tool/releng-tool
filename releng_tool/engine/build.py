# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.api import RelengBuildOptions
from releng_tool.defs import PackageType
from releng_tool.engine.autotools.build import build as build_autotools
from releng_tool.engine.cmake.build import build as build_cmake
from releng_tool.engine.python.build import build as build_python
from releng_tool.engine.script.build import build as build_script
from releng_tool.util import nullish_coalescing as NC
from releng_tool.util.api import replicate_package_attribs
from releng_tool.util.io import interim_working_dir
from releng_tool.util.log import err
from releng_tool.util.log import note
import sys

def stage(engine, pkg, script_env):
    """
    handles the build stage for a package

    With a provided engine and package instance, the build stage will be
    processed.

    Args:
        engine: the engine
        pkg: the package being built
        script_env: script environment information

    Returns:
        ``True`` if the build stage is completed; ``False`` otherwise
    """

    note('building {}...'.format(pkg.name))
    sys.stdout.flush()

    if pkg.build_subdir:
        build_dir = pkg.build_subdir
    else:
        build_dir = pkg.build_dir

    build_opts = RelengBuildOptions()
    replicate_package_attribs(build_opts, pkg)
    build_opts.build_defs = pkg.build_defs
    build_opts.build_dir = build_dir
    build_opts.build_env = pkg.build_env
    build_opts.build_opts = pkg.build_opts
    build_opts.build_output_dir = pkg.build_output_dir
    build_opts.def_dir = pkg.def_dir
    build_opts.env = script_env
    build_opts.ext = pkg.ext_modifiers
    build_opts.host_dir = engine.opts.host_dir
    build_opts.name = pkg.name
    build_opts.prefix = NC(pkg.prefix, engine.opts.sysroot_prefix)
    build_opts.staging_dir = engine.opts.staging_dir
    build_opts.symbols_dir = engine.opts.symbols_dir
    build_opts.target_dir = engine.opts.target_dir
    build_opts.version = pkg.version
    build_opts._quirks = engine.opts.quirks

    # if package has a job-override value, use it over any global option
    if pkg.fixed_jobs:
        build_opts.jobs = pkg.fixed_jobs
        build_opts.jobsconf = pkg.fixed_jobs
    else:
        build_opts.jobs = engine.opts.jobs
        build_opts.jobsconf = engine.opts.jobsconf

    builder = None
    if pkg.type in engine.registry.package_types:
        def _(opts):
            return engine.registry.package_types[pkg.type].build(pkg.type, opts)
        builder = _
    elif pkg.type == PackageType.AUTOTOOLS:
        builder = build_autotools
    elif pkg.type == PackageType.CMAKE:
        builder = build_cmake
    elif pkg.type == PackageType.PYTHON:
        builder = build_python
    elif pkg.type == PackageType.SCRIPT:
        builder = build_script

    if not builder:
        err('build type is not implemented: {}'.format(pkg.type))
        return False

    with interim_working_dir(build_dir):
        built = builder(build_opts)
        if not built:
            return False

    return True
