# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.api import RelengConfigureOptions
from releng_tool.defs import PackageInstallType
from releng_tool.defs import PackageType
from releng_tool.engine.autotools.configure import configure as conf_autotools
from releng_tool.engine.cmake.configure import configure as conf_cmake
from releng_tool.engine.make.configure import configure as conf_make
from releng_tool.engine.meson.configure import configure as conf_meson
from releng_tool.engine.scons.configure import configure as conf_scons
from releng_tool.engine.script.configure import configure as conf_script
from releng_tool.util import nullish_coalescing as NC
from releng_tool.util.api import replicate_package_attribs
from releng_tool.util.io_wd import wd
from releng_tool.util.log import err
from releng_tool.util.log import note


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

    note('configuring {}...', pkg.name)

    # ignore configuration step for types which do not have one
    ignored_types = [
        PackageType.CARGO,
        PackageType.PYTHON,
    ]
    if pkg.type in ignored_types:
        return True

    if pkg.build_subdir:
        build_dir = pkg.build_subdir
    else:
        build_dir = pkg.build_dir

    pkg_install_type = NC(pkg.install_type, PackageInstallType.TARGET)

    configure_opts = RelengConfigureOptions()
    replicate_package_attribs(configure_opts, pkg)
    configure_opts.build_base_dir = engine.opts.build_dir
    configure_opts.build_dir = build_dir
    configure_opts.build_output_dir = pkg.build_output_dir
    configure_opts.conf_defs = pkg.conf_defs
    configure_opts.conf_env = pkg.conf_env
    configure_opts.conf_opts = pkg.conf_opts
    configure_opts.def_dir = pkg.def_dir
    configure_opts.env = script_env
    configure_opts.ext = pkg.ext_modifiers
    configure_opts.host_dir = engine.opts.host_dir
    configure_opts.install_type = pkg_install_type
    configure_opts.name = pkg.name
    configure_opts.prefix = NC(pkg.prefix, engine.opts.sysroot_prefix)
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
        configurer = conf_autotools
    elif pkg.type == PackageType.CMAKE:
        configurer = conf_cmake
    elif pkg.type == PackageType.MAKE:
        configurer = conf_make
    elif pkg.type == PackageType.MESON:
        configurer = conf_meson
    elif pkg.type == PackageType.SCONS:
        configurer = conf_scons
    elif pkg.type == PackageType.SCRIPT:
        configurer = conf_script

    if not configurer:
        err('configurer type is not implemented: {}', pkg.type)
        return False

    with wd(build_dir):
        configured = configurer(configure_opts)
        if not configured:
            return False

    return True
