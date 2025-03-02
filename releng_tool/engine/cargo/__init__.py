# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from configparser import ConfigParser
from releng_tool.defs import VcsType
from releng_tool.tool.cargo import CARGO
from releng_tool.util.io_wd import wd
from releng_tool.util.log import debug
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
import os
import posixpath


# folder name (under build) where all cargo packages will target
CARGO_COMMON_TARGET = '.releng-tool-cargo-target'

# manifest for cargo packges
CARGO_MANIFEST = 'Cargo.toml'


def cargo_package_clean(opts, pkg):
    """
    perform a cargo package clean

    Cargo packages are treated differently for a build. Instead of having
    each Cargo package being contained in their own build directory, we
    "need" to place them into a common target (i.e. CARGO_COMMON_TARGET).
    Cargo has its own world for dealing with profile building, and there
    is no graceful way to manipulate Cargo to process packages to use
    releng-tool package-specific build directories along with a separate
    staging folder.

    Instead, we have all Cargo packages use a shared target directory.
    This can allow Cargo to build these packages together, versus having
    to rebuild each component per package. This does complicate releng-tool's
    package-specific clean capability, since it is more than just removing
    the build directory contents. To deal with this, this call can be made
    before cleaning the build directory to invoke a `cargo clean` call for the
    specific package. Ideally, this will remove just the package-specific
    content from within this common target folder.

    Args:
        opts: build options
        pkg: the package
    """

    if pkg.build_subdir:
        build_dir = pkg.build_subdir
    else:
        build_dir = pkg.build_dir

    # only attempt to
    if not os.path.exists(os.path.join(build_dir, CARGO_MANIFEST)):
        return

    cargo_args = [
        'clean',
        # provide an explicit cargo path (to prevent cargo from searching)
        '--manifest-path',
        CARGO_MANIFEST,
        # never perform online interaction in build stage
        '--offline',
        # configure target directory to this package's output folder
        '--target-dir',
        os.path.join(opts.build_dir, CARGO_COMMON_TARGET),
        # clean the specific package
        '--package',
        pkg.cargo_name,
    ]

    # controlled dependencies... but be flexible for local projects
    if pkg.vcs_type != VcsType.LOCAL:
        cargo_args.append('--locked')

    # If the package does not define a specific profile to run, assume a
    # default "release" build.
    if not pkg.build_opts or '--profile' not in pkg.build_opts:
        cargo_args.append('--release')

    # invoke a package-specific clean
    with wd(build_dir):
        if not CARGO.execute(cargo_args):
            warn('failed to clean cargo contents: {}', pkg.name)


def cargo_register_pkg_paths(pkgs):
    """
    populate patch configuration arguments for cargo packages

    For Cargo packages used in releng-tool, dependencies are typical vendored
    from crates.io. However, users may have specific dependencies they want
    to manage/use in a releng-tool project itself. A project can define
    Cargo library definitions and have them build as normal, however, we
    need a means to inform Cargo where to find these Cargo library
    definitions, instead of looking online. This can be achieved by
    generating patch configurations for these packages. This call will scan
    for dependencies of a Cargo package and check if the dependency is
    managed by the releng-tool project. If so, patch arguments will be
    generated and used when processing the Cargo package.

    Args:
        pkgs: cargo-specific packages to scan/populate patch arguments
    """

    # compile a list of potential path overrides to forward
    cargo_pkgs = []
    cargo_patches = {}

    for pkg in pkgs:
        cmf = os.path.join(pkg.build_tree, CARGO_MANIFEST)
        if not os.path.exists(cmf):
            debug('could not find cargo manifest for package: {}', pkg.name)
            continue

        cargo_pkgs.append(pkg)

        cpth = pkg.build_tree.replace(os.sep, posixpath.sep)
        cargo_patches[pkg.cargo_name] = \
            f'patch.crates-io."{pkg.cargo_name}".path="{cpth}"'

    # extract all known dependencies from each cargo package
    cargo_deps = {}

    for pkg in cargo_pkgs:
        parser = ConfigParser()
        cmf = os.path.join(pkg.build_tree, CARGO_MANIFEST)

        parser.read(cmf)
        if parser.has_section('dependencies'):
            for dependency in parser.options('dependencies'):
                cargo_deps.setdefault(pkg.cargo_name, []).append(dependency)

            if pkg.cargo_name in cargo_deps:
                debug('detected cargo dependencies ({}): {}', pkg.name,
                    ', '.join(cargo_deps[pkg.cargo_name]))

    # build dependency chains for each individual cargo package; we will
    # need to provide each their own patch argument set for every package
    # they depend on (explicitly and through their own dependencies)
    for pkg in cargo_pkgs:
        scan = cargo_deps.get(pkg.cargo_name, [])[:]
        seen = set(scan)

        while scan:
            dependency = scan.pop()

            for subdep in cargo_deps.get(dependency, []):
                if subdep not in seen:
                    scan.append(subdep)

            patch_arg = cargo_patches.get(dependency)
            if patch_arg:
                verbose('prepared cargo patch ({}): {}', pkg.name, dependency)
                pkg.cargo_depargs.append('--config')
                pkg.cargo_depargs.append(patch_arg)
