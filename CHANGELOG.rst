Development
-----------

- Adding ``dst_dir`` to ``releng_copy`` for explicit copies to directories
- Fixed an issue where forced git-fetches with branch revisions may have stale
  content on first extract
- Fixed where package-specific prefixes/njobs would leak to other projects
- Introduce ``*_[INCLUDE,LIB]_DIR`` environment/script variables
- Introduce ``PKG_BUILD_BASE_DIR`` environment/script variable
- Introduce ``PREFIXED_*_DIR`` environment/script variables
- Introduce ``releng_include`` helper script function
- Support make-styled environment injections via command line
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
- Fixed an issue where extensions may not load on python 2.7
- Fixed an issue where post-processing may be invoked even if a package's stage
  would fail
- Introduce ``<PKG_NAME>_DEFDIR`` environment/script variable
- Introduce ``LIBFOO_CMAKE_NOINSTALL`` for cmake packages with no install rule
- Introduce support for rsync sites
- Provide an option to suppress root warning (for zero-uid containers)
- Remove the requirement to have a package version entry
- Support configuring cache/download directories using environment variables
- Support custom ssl context overrides via ``urlopen_context``
- Support providing an assets container directory (for cache/download folders)

0.9 (2021-10-02)
----------------

- Fixed an import issue when running with python 3.10
- Fixed an issue where a cyclic package check provided a bad message
- Fixed an issue where a git submodule with a target branch may fail to extract
- Post-processing script renamed to ``releng-post-build``
- Support development mode relaxed branch fetching for git sites
- Support requiring a git source's revision to be gpg-signed
- Support using ascii-armor (asc) files to package integrity checks

0.8 (2021-08-28)
----------------

- Allow dvcs packages to share caches (to minimize space/time fetching)
- Fixed an issue where tools/``releng_execute`` requests would fail on python
  2.7 with unicode-defined environment variables
- Fixed an issue where a diverged revision in git would incorrectly populate a
  package's build directory with the cached revision instead of the remote
  revision
- Introduce ``LIBFOO_GIT_SUBMODULES`` for package git-specific configurations
- Introduce ``releng_execute_rv`` helper script function
- Introduce statistic tracking (stage durations) which generate to into the
  output folder after execution
- Introduce support for package-specific distclean
- Introduce support for package-specific license processing
- Package-specific extraction/patching no longer requires dependency processing
- Rework ``LIBTOOL_GIT_REFSPECS`` to provide more control over custom revisions
  that can be fixed (i.e. no longer fixed on ``<target>/*/head``; instead, a
  configured value-wildcard string should be used)
- Support auto-detecting python interpreter path overrides in windows
- Support faster git fetching
- Support pruning any remote-tracked references in a git-cached project when a
  forced fetch request is made

0.7 (2021-08-08)
----------------

- Fetch from an already cached package's site if the fetch is explicitly
  requested
- Fixed an issue with registry failing to import on python 2.7
- Fixed issue where build/install definitions where not used in in their
  respective stages
- Fixed issue where mercurial packages fetched using the version option instead
  of the revision option
- Fixed issue where the host directory was not registered in a stage's path
- Introduce clean, logging flags and releng-version into the script environments
- Only fetch a single package if only said package is requested to be fetched
- Package without a site will throw an error when vcs-type is set
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

- Fixed false error when verifying cached git reference

0.4 (2020-09-07)
----------------

- Allow developers to fetch from addition git refspecs (e.g. pull requests)
- Allow setting quirks in command line
- Fixed a scenario where a git extraction stage could fetch sources
- Fixed git fetch/extraction if package is cached and site has changed
- Improved handling of output files which may set the readonly attribute
- Introduce support for local interim-development package content
- Introduce support for shallow git fetching

0.3 (2019-10-19)
----------------

- Allow packages to configure to ignore cache while in development mode
- Allow packages to configure for no-extraction for sources
- Fixed default interpreter detection for python packages
- Fixed fetching from mercurial sources
- Fixed fetching from newer git hashes if repository was already cached
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
