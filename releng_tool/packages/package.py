# -*- coding: utf-8 -*-
# Copyright 2018-2022 releng-tool

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
        host_provides: host tools the package will provide
        install_type: install container for the package (target, staged, etc.)
        is_internal: whether or not this package is an project internal package
        license: license(s) of the package
        license_files: list of files in sources holding license information
        local_srcs: whether this package is acquired locally
        name: name of the package
        no_extraction: whether or not this package will extract
        nv: name-version value of the package
        prefix: system root prefix override (if applicable)
        revision: revision to use to fetch from vcs (if applicable)
        site: site to acquire package assets
        skip_remote_config: whether or not to skip any remote configuration
        skip_remote_scripts: whether or not to skip any remote scripts
        strip_count: archive extraction strip count (if applicable)
        type: package type (script-based, cmake, etc.)
        vcs_type: vcs type of the package (git, file, etc.)
        version: package version
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
        (package type - cmake)
        cmake_noinstall: flag to disable the install stage for a cmake project
        (package type - make)
        make_noinstall: flag to disable the install stage for a make project
        (other - python)
        python_interpreter: python interpreter to invoke stages with
    """
    def __init__(self, name, version):
        self.name = name
        self.version = version
        if version:
            self.nv = '{}-{}'.format(name, version)
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
        self.host_provides = None
        self.ext_modifiers = None
        self.extract_type = None
        self.install_type = None
        self.is_internal = None
        self.license = None
        self.license_files = None
        self.local_srcs = False
        self.no_extraction = False
        self.prefix = None
        self.revision = None
        self.site = None
        self.skip_remote_config = None
        self.skip_remote_scripts = None
        self.strip_count = None
        self.type = None
        self.vcs_type = None
        # (package type - common)
        self.build_defs = None
        self.build_env = None
        self.build_opts = None
        self.conf_defs = None
        self.conf_env = None
        self.conf_opts = None
        self.install_defs = None
        self.install_env = None
        self.install_opts = None
        # (package type - autotools)
        self.autotools_autoreconf = None
        # (package type - cmake)
        self.cmake_noinstall = None
        # (package type - make)
        self.make_noinstall = None
        # (other - git)
        self.git_config = None
        self.git_depth = None
        self.git_refspecs = None
        self.git_submodules = None
        self.git_verify_revision = None
        # (other - python)
        self.python_interpreter = None
