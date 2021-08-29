0.8 (2021-08-28)
----------------

- allow dvcs packages to share caches (to minimize space/time fetching)
- fixed an issue where tools/``releng_execute`` requests would fail on python
  2.7 with unicode-defined environment variables
- fixed an issue where a diverged revision in git would incorrectly populate a
  package's build directory with the cached revision instead of the remote
  revision
- introduce ``LIBFOO_GIT_SUBMODULES`` for package git-specific configurations
- introduce ``releng_execute_rv`` helper script function
- introduce statistic tracking (stage durations) which generate to into the
  output folder after execution
- introduce support for package-specific distclean
- introduce support for package-specific license processing
- rework ``LIBTOOL_GIT_REFSPECS`` to provide more control over custom revisions
  that can be fixed (i.e. no longer fixed on ``<target>/*/head``; instead, a
  configured value-wildcard string should be used)
- support auto-detecting python interpreter path overrides in windows
- support faster git fetching
- support pruning any remote-tracked references in a git-cached project when a
  forced fetch request is made
- package-specific extraction/patching no longer requires dependency processing

0.7 (2021-08-08)
----------------

- fetch from an already cached package's site if the fetch is explicitly
  requested
- fixed an issue with registry failing to import on python 2.7
- fixed issue where build/install definitions where not used in in their
  respective stages
- fixed issue where mercurial packages fetched using the version option instead
  of the revision option
- fixed issue where the host directory was not registered in a stage's path
- introduce clean, logging flags and releng-version into the script environments
- only fetch a single package if only said package is requested to be fetched
- package without a site will throw an error when vcs-type is set
- reconfigure/rebuild requests will now perform all trailing stages for the
  package(s) being redone; rebuild/reconfigure-only actions have been introduced
  to force re-invoking a specific stage
- releng-tool will now full stop if external package definition fails to load
- support loading remote package configuration
- support loading remote package scripts

0.6 (2020-10-10)
----------------

- always register optional flags inside scripts (allowing developers to use
  flags like ``RELENG_RECONFIGURE`` without needing to check environment
  variables)
- fixed issued when capturing with ``releng_execute`` which did not suppress
  output by default
- introduce ``LIBTOOL_GIT_CONFIG`` for package git-specific configurations
- introduce a ``releng-tool init`` action for a quick-sample project
- introduce support for distclean
- introduce support for prerequisites
- namespace moved from ``releng`` to ``releng_tool`` (``releng`` deprecated for
  an interim)

0.5 (2020-09-07)
----------------

- fixed false error when verifying cached git reference

0.4 (2020-09-07)
----------------

- allow developers to fetch from addition git refspecs (e.g. pull requests)
- allow setting quirks in command line
- fixed a scenario where a git extraction stage could fetch sources
- fixed git fetch/extraction if package is cached and site has changed
- improved handling of output files which may set the readonly attribute
- introduce support for local interim-development package content
- introduce support for shallow git fetching

0.3 (2019-10-19)
----------------

- allow packages to configure to ignore cache while in development mode
- allow packages to configure for no-extraction for sources
- fixed default interpreter detection for python packages
- fixed fetching from mercurial sources
- fixed fetching from newer git hashes if repository was already cached
- introduce ``releng_env`` and ``releng_mkdir`` helper script functions
- introduce support for package-specific bootstrapping stage

0.2 (2019-03-15)
----------------

- a project's host directory will now be registered in the system's path during
  execution
- allow tracking project's license files when found in multiple directories
- fixed loading configuration overrides script if one actually exists
- re-work various script names (e.g. ``releng.py`` -> ``releng``)

0.1 (2019-02-24)
----------------

- hello world
