# releng-tool

[![pip Version](https://badgen.net/pypi/v/releng-tool?label=PyPI)](https://pypi.python.org/pypi/releng-tool)
[![Supports all Python versions](https://badgen.net/static/Python/2.7%20%7C%203.4-3.12)](https://pypi.python.org/pypi/releng-tool)
[![Build Status](https://github.com/releng-tool/releng-tool/actions/workflows/build.yml/badge.svg)](https://github.com/releng-tool/releng-tool/actions/workflows/build.yml)
[![Tools Status](https://github.com/releng-tool/releng-tool/actions/workflows/check-tools.yml/badge.svg)](https://github.com/releng-tool/releng-tool/actions/workflows/check-tools.yml)
[![Documentation](https://badgen.net/badge/Documentation/releng.io/333333)](https://docs.releng.io) 

## Overview

When dealing with a project that depends on multiple packages, assets may be
found in multiple locations and may require various methods to extract, build
and more. releng-tool can be used to process a defined set of
projects/packages which identify where resources can be fetched, how packages
can be extracted and methods to patch, configure, build and install each
individual package for a target root.

For detailed documentation on the releng-tool project, see
[releng-tool's documentation][releng-tool-doc].

## Requirements

* [Python][python] 2.7 or 3.4+

Host tools such as [Git][git], scp, etc. may be required depending on the
project being processed (e.g. if a package's sources fetch from a Git source,
a Git client tool is required to perform said fetch).

## Installation

This tool can be installed using [pip][pip]:

```shell
pip install releng-tool
 (or)
python -m pip install releng-tool
```

For Arch Linux users, this package is also available on AUR:

> Arch User Repository - releng-tool \
> https://aur.archlinux.org/packages/releng-tool/

## Usage

This tool can be invoked from a command line using:

```shell
releng-tool --help
 (or)
python -m releng-tool --help
```

## Examples

Examples of releng-tool projects can be found in
[releng-tool's examples repository][releng-tool-examples].

[git]: https://git-scm.com/
[pip]: https://pip.pypa.io/
[python]: https://www.python.org/
[releng-tool-doc]: https://docs.releng.io/
[releng-tool-examples]: https://github.com/releng-tool/releng-tool-examples
