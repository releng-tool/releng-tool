releng-tool
===========

.. image:: https://badgen.net/pypi/v/releng-tool?label=PyPI
    :target: https://pypi.python.org/pypi/releng-tool
    :alt: pip Version

.. image:: https://badgen.net/pypi/python/releng-tool?label=Python
    :target: https://pypi.python.org/pypi/releng-tool
    :alt: Supports all Python versions

.. image:: https://badgen.net/badge/Documentation/releng.io/333333
    :target: https://docs.releng.io
    :alt: Documentation

.. raw:: html

   <br/>

.. image:: https://github.com/releng-tool/releng-tool/actions/workflows/build.yml/badge.svg
    :target: https://github.com/releng-tool/releng-tool/actions/workflows/build.yml
    :alt: Build Status

.. image:: https://github.com/releng-tool/releng-tool/actions/workflows/check-tools.yml/badge.svg
    :target: https://github.com/releng-tool/releng-tool/actions/workflows/check-tools.yml
    :alt: Tools Status

.. image:: https://github.com/releng-tool/releng-tool/actions/workflows/doc-update.yml/badge.svg
    :target: https://github.com/releng-tool/releng-tool/actions/workflows/doc-update.yml
    :alt: Documentation Status

Overview
--------

When dealing with a project that depends on multiple packages, assets may be
found in multiple locations and may require various methods to extract, build
and more. releng-tool can be used to process a defined set of
projects/packages which identify where resources can be fetched, how packages
can be extracted and methods to patch, configure, build and install each
individual package for a target root.

For detailed documentation on the releng-tool project, see
`releng-tool's documentation`_.

Requirements
------------

* Python_ 2.7 or 3.4+

Host tools such as Git_, scp, etc. may be required depending on the project
being processed (e.g. if a package's sources fetch from a Git source, a Git
client tool is required to perform said fetch).

Installation
------------

This tool can be installed using pip_:

.. code-block:: shell

   pip install releng-tool
    (or)
   python -m pip install releng-tool

For Arch Linux users, this package is also available on AUR:

 | Arch User Repository - releng-tool
 | https://aur.archlinux.org/packages/releng-tool/

Usage
-----

This tool can be invoked from a command line using:

.. code-block:: shell

   releng-tool --help
    (or)
   python -m releng_tool --help

Examples
--------

Examples of releng-tool projects can be found in
`releng-tool's examples repository`_.

.. _Git: https://git-scm.com/
.. _Python: https://www.python.org/
.. _pip: https://pip.pypa.io/
.. _releng-tool's documentation: https://docs.releng.io/
.. _releng-tool's examples repository: https://github.com/releng-tool/releng-tool-examples
