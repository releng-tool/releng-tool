2.0.1 (2025-02-09)
------------------

- Including missing completion scripts and man page in source package

2.0 (2025-02-09)
----------------

- **(note)** Support for non-LTS version of Python have been dropped
- Fixed handling of Git submodules using incorrect revisions
- Fixed issue where configured prefixes could be ignored in Python packages
- Fixed issue where file URIs sites may prevent other URL sites from fetching
- Fixed issue where triggering a re-install on select Python packages would fail
- Improved support for host tool integration with Python packages
- Introduce `--only-mirror` argument to force external package fetch with mirror
- Introduce alternative hash-files for package development revisions
- Overhaul of Python package processing with install scheme configuration
  via ``LIBFOO_PYTHON_INSTALLER_SCHEME``, launcher configuration via
  ``LIBFOO_PYTHON_INSTALLER_LAUNCHER_KIND`` and dist overrides via
  ``LIBFOO_PYTHON_DIST_PATH``
- Script function ``releng_ls`` now accepts a ``recursive`` argument
- Support URL fetch retries on transient errors
- Support for GNU Bazaar sites is deprecated
- Support for Python distutils packages is deprecated
- Support for ``override_revisions`` is deprecated
- Support for ``override_sites`` is deprecated
- Support format hints in ``url_mirror``
- Support ignoring ``stderr`` output in execute calls
- Support maximum checks when using ``releng_require_version``
- Use of Python's ``installer`` required for all Python packages

1.4 (2025-01-19)
----------------

- Allow adding a package without a definition that defines at least one script
- Allow users to suppress local-site package warnings
- Correct ``hint`` missing from script environments
- Disable garbage collection and maintenance tasks for Git caches
- Disable update checks for PDM when processing PDM packages
- Ensure the ``punch`` action triggers the post-build stage
- Fixed configuration failure when using older Meson (pre-v1.1.1)
- Fixed incorrect JSON/SPDX SBOM documents for projects with empty/local sites
- Fixed issue where ``releng_copy`` could not copy a broken symbolic link
- Fixed issue where ``releng_remove`` could not remove a broken symbolic link
- Fixed patch overrides not supporting alternative file extensions
- Flag ``RELENG_FORCE`` when using the ``punch`` action
- Introduce ``LIBFOO_CARGO_NOINSTALL`` to support Cargo libraries
- Introduce ``RELENG_EXEC`` environment/script variable
- Introduce ``libfoo-fresh`` action
- Introduce ``releng_symlink`` helper script function
- Introduce a ``nested`` option for I/O copy/move utility calls
- Introduce a shared build target for Cargo packages
- Perform automatic Cargo patching for project-managed dependencies
- Post-fetching Cargo dependencies now occurs after a package's patch stage
- Promote use of ``.rt`` extensions for definitions/scripts
- Promote use of ``releng-tool.rt`` for project configuration
- Support Breezy VCS-type
- Support injecting Visual Studio development environment variables
- Support newer GitLab CI flag for automatic debugging mode
- Support preallocated list/dictionary package configurations
- Update SPDX license database to v3.26
- Utilize forwarded arguments as fallback for ``libfoo-exec`` action

1.3 (2024-08-19)
----------------

- Automatic debugging mode when detecting CI debugging runs
- Correct unexpected dot in prefix path variables for empty prefixed builds
- Fixed incorrect specification version tag in RDF/SPDX SBOM documents
- Fixed issue where an aborted Mercurial fetch could require manual cleanup
- Include license list version in SPDX SBOM documents
- Introduce ``LIBFOO_NEEDS`` to replace ``LIBFOO_DEPENDENCIES``
- Introduce ``RELENG_GENERATED_LICENSES`` script variable
- Introduce ``RELENG_GENERATED_SBOMS`` script variable
- Introduce ``environment`` project configuration
- Introduce support for Cargo-based packages
- Remote package configuration/scripting is now opt-in
- Script helper ``releng_mkdir`` will now return the path
- Support multiple path components in ``releng_mkdir``
- Support variable expansion for ``releng_execute`` arguments
- Unknown arguments will now generate an error by default
- Update SPDX license database to v3.25

1.2 (2024-07-01)
----------------

- Introduce the ``punch`` action to support forced rebuild of packages
- Support automatic package preparation for compatible local-sourced packages
- Update SPDX license database to v3.24

1.1 (2024-03-29)
----------------

- Prevent SSH authentication prompts that may occur when using Git
- Support SPDX license identifier field for custom licenses
- Support environment output directory override (``RELENG_OUTPUT_DIR``)
- Support global output containers (``RELENG_GLOBAL_OUTPUT_CONTAINER_DIR``)
- Update SPDX license database to v3.23

1.0 (2023-12-22)
----------------

- Introduce ``RELENG_SCRIPT`` and ``RELENG_SCRIPT_DIR`` variables
- Update SPDX license database to v3.22

0.17 (2023-08-06)
-----------------

- Fixed issue with CMake-generated export targets missing prefix overrides
- Fixed issue with local-source configurations when provided relative paths
- Introduce ``LIBFOO_CMAKE_BUILD_TYPE`` to override CMake build types
- Introduce ``LIBFOO_ENV`` to apply environment variables on multiple stages
- Introduce ``state`` action for dumping configured releng-tool state
- Introduce support for Perforce sites
- Support Git repository interaction in output directories for Git-based sources
- Support ability to unconfigure development/local-sources mode
- Support the existence of a ``NO_COLOR`` environment variable
- Update SPDX license database to v3.21

0.16 (2023-05-07)
-----------------

- Enforce strict hash checking in development mode for external packages which
  define a development revision
- Fixed issue where ``releng_copy`` may fail when provided a single part
  relative destination
- Fixed issue where HTML-based software build of materials would be empty
- Introduce support for Meson-based packages
- Prevent processing packages when SBOM generation is explicitly requested
- Support SPDX-tailored software build of materials
- Support module-specific local-sources to accept ``:`` instead of ``@``,
  allowing certain shells to take advantage of path auto-completion

0.15 (2023-02-12)
-----------------

- CMake install events will now always skip dependency checks
- Fixed issue where extension loading may cause issues in Python 2.7
- Fixed issue where reconfiguration may not flag rebuild flags (and related)
- Fixed issue where statistics (PDF) may fail on legacy matplotlib environments
- Improve support for patching a root build directory and sub-directories
- Introduce extension support for event listeners
- Make projects will now be provided a ``PREFIX`` override
- Source distribution now includes completion scripts and tests
- Support setting software build of materials format in project configuration

0.14 (2023-02-05)
-----------------

- **(note)** The deprecated ``releng`` namespace has been removed
- CMake install events will now always force installs by default
- Fixed issue where CMake projects with implicit target area installs have
  issues finding includes/libraries with ``find_<x>`` calls
- Fixed issue where ``libfoo-exec`` action with an ``=`` character would crash
- Introduce ``*_BIN_DIR`` environment/script variables
- Introduce ``releng_move_into`` helper script function
- Local VCS-type packages should now place sources inside a ``local`` folder
- Promote the use of SPDX license identifiers in package license options
- Support ``.releng`` extensions for scripts
- Support automatic include injection for CMake staging/target/host areas
- Support for Poetry Python setup type
- Support generating a software build of materials
- Support treating releng-tool warnings as errors with ``--werror`` argument
- Support user paths in package-specific local-sources overrides

0.13 (2022-08-10)
-----------------

- Avoid interaction with target area when using CMake projects that only
  uses the staging area
- Downloaded files will now be stored in sub-directories under ``dl/``
- Ensure clean-related environment/script variables are set for
  package-specific clean requests
- Fixed a rare chance that an explicit package run provided via command line
  may be ignored
- Fixed issue in older Python interpreters where the executed package order may
  not be consistent
- Fixed issue where select package-specific environment variables may leak into
  other packages
- Improve handling of ``file://`` sites in Windows
- Improve support for host-built Python packages
- Introduce ``LIBFOO_HOST_PROVIDES`` to help skip prerequisite checks
- Introduce ``PKG_DEVMODE`` environment/script variable
- Introduce ``RELENG_TARGET_PKG`` environment/script variable
- Introduce ``releng_copy_into`` helper script function
- Introduce support for Python setup types
- Introduce support for SCons-based packages
- Introduce support for development mode configurations, allowing users
  to target specific revisions or sites for packages supporting alternative
  source revisions
- Introduce support for global and package-specific path overrides when
  operating in local-sources mode
- Introduce support for make-based packages
- Support ``PKG_DEFDIR`` usage inside a package's definition
- Support Bazaar quirk to utilize ``certifi`` certificates
- Support users overriding a project's configuration path from command line

0.12 (2022-05-02)
-----------------

- Adding ``dst_dir`` to ``releng_copy`` for explicit copies to directories
- Adjust automatic job detection to use physical cores instead of logical cores
- Fixed an issue where forced Git-fetches with branch revisions may have stale
  content on first extract
- Fixed where package-specific prefixes/njobs would leak to other projects
- Introduce ``*_[INCLUDE,LIB]_DIR`` environment/script variables
- Introduce ``PKG_BUILD_BASE_DIR`` environment/script variable
- Introduce ``PREFIXED_*_DIR`` environment/script variables
- Introduce ``libfoo-exec`` action
- Introduce ``releng_include`` helper script function
- Support Make-styled environment injections via command line
- Support package variable overrides via command line

0.11 (2022-02-26)
-----------------

- Always pre-create install directory before package install scripts are invoked
- Fixed an issue where nested zip files could not extract
- Introduce ``releng_cat`` helper script function
- Introduce ``releng_ls`` helper script function
- Introduce ``releng_require_version`` helper script function
- No longer extract with non-local-supported tar command if host format detected
- No longer warn if hash file is empty for extracted contents check
- Support removing cached assets through a forced fetch argument
- Support triggering a reconfiguration of all packages through a force argument

0.10 (2021-12-31)
-----------------

- Fixed an issue where a configured ``sysroot_prefix`` bin path would not be
  registered in the script environment's path
- Fixed an issue where ``releng_mkdir`` reports success if the target path is a
  file that already exists
- Fixed an issue where extensions may not load on Python 2.7
- Fixed an issue where post-processing may be invoked even if a package's stage
  would fail
- Introduce ``<PKG_NAME>_DEFDIR`` environment/script variable
- Introduce ``LIBFOO_CMAKE_NOINSTALL`` for CMake packages with no install rule
- Introduce support for rsync sites
- Provide an option to suppress root warning (for zero-uid containers)
- Remove the requirement to have a package version entry
- Support configuring cache/download directories using environment variables
- Support custom SSL context overrides via ``urlopen_context``
- Support providing an assets container directory (for cache/download folders)

0.9 (2021-10-02)
----------------

- Fixed an import issue when running with Python 3.10
- Fixed an issue where a cyclic package check provided a bad message
- Fixed an issue where a Git submodule with a target branch may fail to extract
- Post-processing script renamed to ``releng-post-build``
- Support development mode relaxed branch fetching for Git sites
- Support requiring a Git source's revision to be GnuPG-signed (GPG)
- Support using ASCII-armor (asc) files to package integrity checks

0.8 (2021-08-28)
----------------

- Allow DVCS packages to share caches (to minimize space/time fetching)
- Fixed an issue where tools/``releng_execute`` requests would fail on Python
  2.7 with Unicode-defined environment variables
- Fixed an issue where a diverged revision in Git would incorrectly populate a
  package's build directory with the cached revision instead of the remote
  revision
- Introduce ``LIBFOO_GIT_SUBMODULES`` for package Git-specific configurations
- Introduce ``releng_execute_rv`` helper script function
- Introduce statistic tracking (stage durations) which generate to into the
  output folder after execution
- Introduce support for package-specific distclean
- Introduce support for package-specific license processing
- Package-specific extraction/patching no longer requires dependency processing
- Rework ``LIBTOOL_GIT_REFSPECS`` to provide more control over custom revisions
  that can be fixed (i.e. no longer fixed on ``<target>/*/head``; instead, a
  configured value-wildcard string should be used)
- Support auto-detecting Python interpreter path overrides in windows
- Support faster Git fetching
- Support pruning any remote-tracked references in a Git-cached project when a
  forced fetch request is made

0.7 (2021-08-08)
----------------

- Fetch from an already cached package's site if the fetch is explicitly
  requested
- Fixed an issue with registry failing to import on Python 2.7
- Fixed issue where build/install definitions where not used in in their
  respective stages
- Fixed issue where mercurial packages fetched using the version option instead
  of the revision option
- Fixed issue where the host directory was not registered in a stage's path
- Introduce clean, logging flags and releng-version into the script environments
- Only fetch a single package if only said package is requested to be fetched
- Package without a site will throw an error when VCS-type is set
- Reconfigure/rebuild requests will now perform all trailing stages for the
  package(s) being redone; rebuild/reconfigure-only actions have been introduced
  to force re-invoking a specific stage
- Support loading remote package configuration
- Support loading remote package scripts
- releng-tool will now full stop if external package definition fails to load

0.6 (2020-10-10)
----------------

- Always register optional flags inside scripts (allowing developers to use
  flags like ``RELENG_RECONFIGURE`` without needing to check environment
  variables)
- Fixed issued when capturing with ``releng_execute`` which did not suppress
  output by default
- Introduce ``LIBTOOL_GIT_CONFIG`` for package git-specific configurations
- Introduce a ``releng-tool init`` action for a quick-sample project
- Introduce support for distclean
- Introduce support for prerequisites
- Namespace moved from ``releng`` to ``releng_tool`` (``releng`` deprecated for
  an interim)

0.5 (2020-09-07)
----------------

- Fixed false error when verifying cached Git reference

0.4 (2020-09-07)
----------------

- Allow developers to fetch from addition Git refspecs (e.g. pull requests)
- Allow setting quirks in command line
- Fixed a scenario where a Git extraction stage could fetch sources
- Fixed Git fetch/extraction if package is cached and site has changed
- Improved handling of output files which may set the readonly attribute
- Introduce support for local interim-development package content
- Introduce support for shallow Git fetching

0.3 (2019-10-19)
----------------

- Allow packages to configure to ignore cache while in development mode
- Allow packages to configure for no-extraction for sources
- Fixed default interpreter detection for Python packages
- Fixed fetching from Mercurial sources
- Fixed fetching from newer Git hashes if repository was already cached
- Introduce ``releng_env`` and ``releng_mkdir`` helper script functions
- Introduce support for package-specific bootstrapping stage

0.2 (2019-03-15)
----------------

- A project's host directory will now be registered in the system's path during
  execution
- Allow tracking project's license files when found in multiple directories
- Fixed loading configuration overrides script if one actually exists
- Re-work various script names (e.g. ``releng.py`` -> ``releng``)

0.1 (2019-02-24)
----------------

- Hello world
