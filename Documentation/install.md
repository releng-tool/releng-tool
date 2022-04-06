# Installation

The recommended method of installing/upgrading releng-tool is using [pip][pip]:

```shell
pip install -U releng-tool
 (or)
python -m pip install -U releng-tool
```

To verify the package has been installed, the following command can be used:

```shell
releng-tool --version
 (or)
python -m releng_tool --version
```

## Quick-start

The following provides a series of steps to assist in preparing a new
environment to use this package.

`````{tab} Linux

While the use of [Python][python]/[pip][pip] is almost consistent between Linux
distributions, the following are a series of helpful steps to install
this package under specific distributions of Linux. From a terminal,
invoke the following commands:

````{tab} Arch

```shell-session
$ sudo pacman -Sy
$ sudo pacman -S python-pip
$ sudo pip install -U releng-tool
$ releng-tool --version
releng-tool <version>
```

This package is also [available on AUR][aur].
````

````{tab} CentOS

```shell-session
$ sudo yum install epel-release
$ sudo yum install python-pip
$ sudo pip install -U releng-tool
$ releng-tool --version
releng-tool <version>
```

````

````{tab} Fedora

```shell-session
$ sudo dnf install python-pip
$ sudo pip install -U releng-tool
$ releng-tool --version
releng-tool <version>
```

````

````{tab} openSUSE

```shell-session
$ pip install releng-tool
$ releng-tool --version
releng-tool <version>
```

````

````{tab} Ubuntu

```shell-session
$ sudo apt update
$ sudo apt install python-pip
$ sudo pip install -U releng-tool
$ releng-tool --version
releng-tool <version>
```

````

`````

````{tab} OS X

From a terminal, invoke the following commands:

```shell-session
$ sudo easy_install pip
$ sudo pip install -U releng-tool
$ releng-tool --version
releng-tool <version>
```

````

````{tab} Windows

If not already installed, download the most recent version of [Python][python]:

> Python -- Downloads \
> <https://www.python.org/downloads/>

When invoking the installer, it is recommended to select the option to
"Add Python to PATH"; however, users can explicitly invoke Python from
an absolute path (the remainder of these steps will assume Python is
available in the path).

Open a Windows command prompt and invoke the following:

```doscon
> python -m pip install -U releng-tool
> python -m releng_tool --version
releng-tool ~version~
```

````

## Development

To install the most recent development sources, the following [pip][pip] command can
be used:

```shell
pip install git+https://github.com/releng-tool/releng-tool.git
```

[aur]: https://aur.archlinux.org/packages/releng-tool/
[python]: https://www.python.org/
[pip]: https://pip.pypa.io/
