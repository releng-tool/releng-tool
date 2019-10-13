master
------

- allow packages to configure to ignore cache while in development mode 
- allow packages to configure for no-extraction for sources
- fixed fetching from mercurial sources
- fixed fetching from newer git hashes if repository was already cached
- introduce ``releng_mkdir`` helper script method
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
