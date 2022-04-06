# Requirements

releng-tool is developed in [Python][python] and requires either
[Python][python] 2.7 or 3.4+ to run. A series of optional tools are
required if certain stages or features are used. For example, projects
fetching sources from [Git][git] will require the `git` tool to be
installed; projects with patches will required the `patch` tool. While
some features may be operating system-specific (e.g. autotools features
are designed for Linux-based hosts), releng-tool can work on multiple
operating system.

[git]: https://git-scm.com/
[python]: https://www.python.org/
