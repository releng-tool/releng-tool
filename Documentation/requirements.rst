Requirements
============

releng-tool is developed in Python_ and requires either Python_ 2.7 or 3.4+ to
run on a host system. A series of optional tools are required if certain stages
and/or features are used. For example, projects fetching sources from Git_ will
require the ``git`` tool installed; projects with patches will required the
``patch`` tool.  While some features may be operating system-specific (e.g.
autotools features are designed for Linux-based hosts), releng-tool can work on
various operating system variants.

.. _Git: https://git-scm.com/
.. _Python: https://www.python.org/
