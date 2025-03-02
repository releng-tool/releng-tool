# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.api import RelengInstallOptions
from releng_tool.defs import PackageInstallType
from releng_tool.defs import PackageType
from releng_tool.engine.autotools.install import install as install_autotools
from releng_tool.engine.cargo.install import install as install_cargo
from releng_tool.engine.cmake.install import install as install_cmake
from releng_tool.engine.make.install import install as install_make
from releng_tool.engine.meson.install import install as install_meson
from releng_tool.engine.python.install import install as install_python
from releng_tool.engine.scons.install import install as install_scons
from releng_tool.engine.script.install import install as install_script
from releng_tool.util import nullish_coalescing as NC
from releng_tool.util.api import replicate_package_attribs
from releng_tool.util.io_wd import wd
from releng_tool.util.log import err
from releng_tool.util.log import note
from releng_tool.util.log import verbose


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

    # check if a package is not using the installation stage
    skip_install = False

    if pkg.type == PackageType.CARGO:
        skip_install = pkg.cargo_noinstall
    elif pkg.type == PackageType.CMAKE:
        skip_install = pkg.cmake_noinstall
    elif pkg.type == PackageType.MAKE:
        skip_install = pkg.make_noinstall
    elif pkg.type == PackageType.MESON:
        skip_install = pkg.meson_noinstall
    elif pkg.type == PackageType.SCONS:
        skip_install = pkg.scons_noinstall

    if skip_install:
        verbose('skipping installation stage for {}', pkg.name)
        return True

    note('installing {}...', pkg.name)

    if pkg.build_subdir:
        build_dir = pkg.build_subdir
    else:
        build_dir = pkg.build_dir

    pkg_install_type = NC(pkg.install_type, PackageInstallType.TARGET)

    if pkg_install_type == PackageInstallType.HOST:
        dest_dirs = [engine.opts.host_dir]
    elif pkg_install_type == PackageInstallType.IMAGES:
        dest_dirs = [engine.opts.images_dir]
    elif pkg_install_type == PackageInstallType.STAGING:
        dest_dirs = [engine.opts.staging_dir]
    elif pkg_install_type == PackageInstallType.STAGING_AND_TARGET:
        dest_dirs = [engine.opts.staging_dir, engine.opts.target_dir]
    else:
        # default to target directory
        dest_dirs = [engine.opts.target_dir]

    install_opts = RelengInstallOptions()
    replicate_package_attribs(install_opts, pkg)
    install_opts.build_base_dir = engine.opts.build_dir
    install_opts.build_dir = build_dir
    install_opts.build_output_dir = pkg.build_output_dir
    install_opts.cache_file = pkg.cache_file
    install_opts.def_dir = pkg.def_dir
    install_opts.dest_dirs = dest_dirs
    install_opts.env = script_env
    install_opts.ext = pkg.ext_modifiers
    install_opts.host_dir = engine.opts.host_dir
    install_opts.images_dir = engine.opts.images_dir
    install_opts.install_defs = pkg.install_defs
    install_opts.install_env = pkg.install_env
    install_opts.install_opts = pkg.install_opts
    install_opts.install_type = pkg_install_type
    install_opts.name = pkg.name
    install_opts.prefix = NC(pkg.prefix, engine.opts.sysroot_prefix)
    install_opts.staging_dir = engine.opts.staging_dir
    install_opts.symbols_dir = engine.opts.symbols_dir
    install_opts.target_dir = engine.opts.target_dir
    install_opts.version = pkg.version
    install_opts._quirks = engine.opts.quirks

    installer = None
    if pkg.type in engine.registry.package_types:
        def _(opts):
            return engine.registry.package_types[pkg.type].install(
                pkg.type, opts)
        installer = _
    elif pkg.type == PackageType.AUTOTOOLS:
        installer = install_autotools
    elif pkg.type == PackageType.CARGO:
        installer = install_cargo
    elif pkg.type == PackageType.CMAKE:
        installer = install_cmake
    elif pkg.type == PackageType.MAKE:
        installer = install_make
    elif pkg.type == PackageType.MESON:
        installer = install_meson
    elif pkg.type == PackageType.PYTHON:
        installer = install_python
    elif pkg.type == PackageType.SCONS:
        installer = install_scons
    elif pkg.type == PackageType.SCRIPT:
        installer = install_script

    if not installer:
        err('installer type is not implemented: {}', pkg.type)
        return False

    with wd(build_dir):
        installed = installer(install_opts)
        if not installed:
            return False

    return True
