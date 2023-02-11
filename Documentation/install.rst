Installation
============

The recommended method of installing/upgrading releng-tool is using pip_:

.. code-block:: shell

   pip install -U releng-tool
    (or)
   python -m pip install -U releng-tool

To verify the package has been installed the following command can be used:

.. code-block:: shell

   releng-tool --version
    (or)
   python -m releng-tool --version

Quick-start
-----------

The following provides a series of steps to assist in preparing a new
environment to use this package.

.. tab:: Linux

    While the use of Python_/pip_ is almost consistent between Linux
    distributions, the following are a series of helpful steps to install
    this package under specific distributions of Linux. From a terminal,
    invoke the following commands:

    .. tab:: Arch

        .. code-block:: shell-session

            $ sudo pacman -Sy
            $ sudo pacman -S python-pip
            $ sudo pip install -U releng-tool
            $ releng-tool --version
            releng-tool <version>

        This package is also
        `available on AUR <https://aur.archlinux.org/packages/releng-tool/>`_.

    .. tab:: CentOS

        .. code-block:: shell-session

            $ sudo yum install epel-release
            $ sudo yum install python-pip
            $ sudo pip install -U releng-tool
            $ releng-tool --version
            releng-tool <version>

    .. tab:: Fedora

        .. code-block:: shell-session

            $ sudo dnf install python-pip
            $ sudo pip install -U releng-tool
            $ releng-tool --version
            releng-tool <version>

    .. tab:: openSUSE

        .. code-block:: shell-session

            $ pip install -U releng-tool
            $ releng-tool --version
            releng-tool <version>

    .. tab:: Ubuntu

        .. code-block:: shell-session

            $ sudo apt update
            $ sudo apt install python-pip
            $ sudo pip install -U releng-tool
            $ releng-tool --version
            releng-tool <version>

.. tab:: OS X

    From a terminal, invoke the following commands:

    .. code-block:: shell-session

        $ sudo easy_install pip
        $ sudo pip install -U releng-tool
        $ releng-tool --version
        releng-tool <version>

.. tab:: Windows

    If not already installed, download the most recent version of Python_:

     | Python - Downloads
     | https://www.python.org/downloads/

    When invoking the installer, it is recommended to select the option to
    "Add Python to PATH"; however, users can explicitly invoked Python from
    an absolute path (the remainder of these steps will assume Python is
    available in the path).

    Open a Windows command prompt and invoke the following:

    .. code-block:: doscon

        > python -m pip install -U releng-tool
        > python -m releng-tool --version
        releng-tool ~version~

Development
-----------

To install the most recent development sources, the following pip_ command can
be used:

.. code-block:: shell

    pip install git+https://github.com/releng-tool/releng-tool.git

.. _Python: https://www.python.org/
.. _pip: https://pip.pypa.io/
