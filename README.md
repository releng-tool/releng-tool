# releng-tool

[![pip Version](https://badgen.net/pypi/v/releng-tool?label=PyPI)](https://pypi.python.org/pypi/releng-tool)
[![Build Status](https://github.com/releng-tool/releng-tool/actions/workflows/build.yml/badge.svg)](https://github.com/releng-tool/releng-tool/actions/workflows/build.yml)
[![Tools Status](https://github.com/releng-tool/releng-tool/actions/workflows/check-tools.yml/badge.svg)](https://github.com/releng-tool/releng-tool/actions/workflows/check-tools.yml)
[![Documentation](https://badgen.net/badge/Documentation/releng.io/333333)](https://docs.releng.io)

## Overview

releng-tool aims to provide a way for developers to tailor the building of
multiple software components to help prepare packages for desired runtime
environments (e.g. cross-platform portable packages, embedded targets, etc.).
When building a package, assets may be located in multiple locations and may
require various methods to extract, build and more. releng-tool allows
developers to define a set of packages, specifying where resources should be
fetched from, how packages should be extracted and the processes for
patching, configuring, building and installing each package for a target
sysroot.

The structure of a package depends on the specific project. The simplest
type is a script-based package, where users can define custom scripts for
various stages. A package does not need to handle every stage. Helper
package types are available (e.g. Autotools, Cargo, CMake, Make, Meson,
various Python types and SCons) for projects using common build systems.

For detailed documentation on the releng-tool project, see
[releng-tool's documentation][releng-tool-doc].

## Requirements

* [Python][python] 3.9+

Host tools such as [Git][git], scp, etc. may be required depending on the
project being processed (e.g. if a package's sources fetch from a Git source,
a Git client tool is required to perform said fetch).

## Installation

This tool can be installed using [pip][pip] or [pipx][pipx]:

```shell
pipx install releng-tool
 (or)
pip install -U releng-tool
 (or)
python -m pip install -U releng-tool
```

For Arch Linux users, this package is also available on AUR:

> Arch User Repository — releng-tool \
> https://aur.archlinux.org/packages/releng-tool/

## Usage

This tool can be invoked from a command line using:

```shell
releng-tool --help
 (or)
python -m releng-tool --help
```

## Demonstration

Users can follow the tutorials found in the documentation:

> releng-tool — Tutorials \
> https://docs.releng.io/getting-started/tutorials/

Or may inspect various test examples demonstrating various capabilities:

> releng-tool — Examples Repository \
> https://github.com/releng-tool/releng-tool-examples


[git]: https://git-scm.com/
[pip]: https://pip.pypa.io/
[pipx]: https://pipx.pypa.io/
[python]: https://www.python.org/
[releng-tool-doc]: https://docs.releng.io/
