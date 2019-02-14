releng-tool
===========

.. image:: https://img.shields.io/pypi/v/releng-tool.svg
    :target: https://pypi.python.org/pypi/releng-tool
    :alt: pip Version

.. image:: https://travis-ci.com/releng-tool/releng-tool.svg?branch=master
    :target: https://travis-ci.com/releng-tool/releng-tool
    :alt: Build Status

releng-tool aims to provide a method to prepare a structured environment to
assist in the release engineering of a project.

overview
--------

When dealing with the release engineering of a project, assets may be found in
multiple locations and may require various methods to extract, build and more.
releng-tool can be used to process a defined set of projects which identifiers
where resources can be fetched, how packages can be extracted and methods to
patch, configure, build and install each individual package for a target root.

.. image:: https://releng.io/assets/overview.png
   :align: center

For detailed documentation on the releng-tool project, please consult the
`releng-tool documentation`_.

requirements
------------

* Python_ 2.7 or 3.4+

Host tools such as Git_, scp, etc. may be required depending on the project
being processed (e.g. if a package's sources fetch from a Git source, a Git
client tool is required to perform said fetch).

installation
------------

This tool can be installed using pip_:

.. code-block:: shell

   pip install releng-tool

.. _Git: https://git-scm.com/
.. _Python: https://www.python.org/
.. _pip: https://pip.pypa.io/
.. _releng-tool documentation: https://docs.releng.io/
