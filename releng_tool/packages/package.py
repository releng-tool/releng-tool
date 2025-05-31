# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

class RelengPackage:
    """
    a releng package

    A package tracks the name, options and dependencies of the package.

    Args:
        name: the name of the package
        version: the version of the package

    Attributes:
        asc_file: file containing ascii-armored data to validate this package
        build_dir: directory for a package's buildable content
        build_output_dir: build output directory for the package process
        build_subdir: override for a package's buildable content (if applicable)
        build_tree: the build tree directory for a package
        cache_dir: cache directory for the package (if applicable)
        cache_file: cache file for the package (if applicable)
        def_dir: directory for the package definition
        deps: list of dependencies for this package
        devmode: whether the package has a devmode revision
        devmode_ignore_cache: whether or not cache files should be ignored
        ext_modifiers: extension-defined modifiers (dict)
        extract_type: extraction type override (for extensions, if applicable)
        fetch_opts: fetch options (if applicable)
        fixed_jobs: fixed job count for this specific package
        git_config: git config options to apply (if applicable)
        git_depth: git fetch depth (if applicable)
        git_refspecs: additional git refspecs to fetch (if applicable)
        git_submodules: fetch any git submodules (if applicable)
        git_verify_revision: verify signed git revisions
        hash_file: file containing hashes to validate this package
        hash_relaxed: whether hash checks can be relaxed
        host_provides: host tools the package will provide
        install_type: install container for the package (target, staged, etc.)
        is_internal: whether or not this package is an project internal package
        license: license(s) of the package
        license_files: list of files in sources holding license information
        local_srcs: whether this package is acquired locally
        name: name of the package
        no_extraction: whether or not this package will extract
        nv: name-version value of the package
        patch_subdir: override for a package's patch base (if applicable)
        prefix: system root prefix override (if applicable)
        remote_config: whether to load any remote configuration
        remote_scripts: whether to process any remote scripts
        revision: revision to use to fetch from vcs (if applicable)
        site: site to acquire package assets
        strip_count: archive extraction strip count (if applicable)
        type: package type (script-based, cmake, etc.)
        vcs_type: vcs type of the package (git, file, etc.)
        version: package version
        vsdevcmd: vsdevcmd configuration
        vsdevcmd_products: vsdevcmd products configuration
        (package type - common)
        build_defs: package-type build definitions
        build_env: package-type build environment overrides
        build_opts: package-type build option overrides
        conf_defs: package-type configuration definitions
        conf_env: package-type configuration environment overrides
        conf_opts: package-type configuration option overrides
        install_defs: package-type installation definitions
        install_env: package-type installation environment overrides
        install_opts: package-type installation option overrides
        (package type - autotools)
        autotools_autoreconf: flag to invoke autoreconf
        (package type - cargo)
        cargo_depargs: generated patch arguments for detected dependencies
        cargo_name: name of the cargo package
        cargo_noinstall: flag to disable the install stage for a cargo project
        (package type - cmake)
        cmake_build_type: cmake build type to use
        cmake_noinstall: flag to disable the install stage for a cmake project
        (package type - make)
        make_noinstall: flag to disable the install stage for a make project
        (package type - meson)
        meson_noinstall: flag to disable the install stage for a meson project
        (other - python)
        python_dist_path: output folder for dist
        python_installer_interpreter: interpreter to use for installation
        python_installer_launcher_kind: launcher kind to use for installation
        python_installer_scheme: scheme to use for installation
        python_interpreter: python interpreter to invoke stages with
        python_setup_type: setup type to build/install with
        (package type - scons)
        scons_noinstall: flag to disable the install stage for a scons project
    """
    def __init__(self, name, version):
        self.name = name
        self.version = version
        if version:
            self.nv = f'{name}-{version}'
        else:
            self.nv = self.name
        # (commons)
        self.asc_file = None
        self.build_dir = None
        self.build_subdir = None
        self.build_output_dir = None
        self.build_tree = None
        self.cache_dir = None
        self.cache_file = None
        self.def_dir = None
        self.deps = []
        self.devmode = None
        self.devmode_ignore_cache = None
        self.fetch_opts = None
        self.fixed_jobs = None
        self.hash_file = None
        self.hash_relaxed = None
        self.host_provides = None
        self.ext_modifiers = None
        self.extract_type = None
        self.install_type = None
        self.is_internal = None
        self.license = None
        self.license_files = None
        self.local_srcs = False
        self.no_extraction = False
        self.patch_subdir = None
        self.prefix = None
        self.remote_config = None
        self.remote_scripts = None
        self.revision = None
        self.site = None
        self.strip_count = None
        self.type = None
        self.vcs_type = None
        self.vsdevcmd = None
        self.vsdevcmd_products = None
        # (package type - common)
        self.build_defs = None
        self.build_env = None
        self.build_env_pkg = None
        self.build_opts = None
        self.conf_defs = None
        self.conf_env = None
        self.conf_env_pkg = None
        self.conf_opts = None
        self.install_defs = None
        self.install_env = None
        self.install_env_pkg = None
        self.install_opts = None
        # (package type - autotools)
        self.autotools_autoreconf = None
        # (package type - cargo)
        self.cargo_depargs = []
        self.cargo_name = None
        self.cargo_noinstall = None
        # (package type - cmake)
        self.cmake_build_type = None
        self.cmake_noinstall = None
        # (package type - make)
        self.make_noinstall = None
        # (package type - meson)
        self.meson_noinstall = None
        # (other - git)
        self.git_config = None
        self.git_depth = None
        self.git_refspecs = None
        self.git_submodules = None
        self.git_verify_revision = None
        # (other - python)
        self.python_dist_path = None
        self.python_installer_interpreter = None
        self.python_installer_launcher_kind = None
        self.python_installer_scheme = None
        self.python_interpreter = None
        self.python_setup_type = None
        # (package type - scons)
        self.scons_noinstall = None
