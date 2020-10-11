master
------

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
