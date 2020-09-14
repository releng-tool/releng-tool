installation
============

The recommended method of installation is using pip_:

.. code-block:: shell

   pip install releng-tool
    (or)
   python -m pip install releng-tool

To verify the package has been installed the following command can be used:

.. code-block:: shell

   releng-tool --version
    (or)
   python -m releng_tool --version

quick-start
-----------

The following provides a series of steps to assist in preparing a new
environment to use this package. This quick-start will aim to use the most
recent version of Python.

linux
~~~~~

While the use of Python_/pip_ is almost consistent between Linux distributions,
the following are a series of helpful steps to install this package under
specific distributions of Linux. From a terminal, invoke the following commands:

arch
++++

.. code-block:: shell

   $ sudo pacman -Sy
   $ sudo pacman -S python-pip
   $ sudo pip install releng-tool
   $ releng-tool --version
   releng-tool <version>

centos
++++++

.. code-block:: shell

   $ sudo yum install epel-release
   $ sudo yum install python-pip
   $ sudo pip install releng-tool
   $ releng-tool --version
   releng-tool <version>

fedora
++++++

.. code-block:: shell

   $ sudo dnf install python-pip
   $ sudo pip install releng-tool
   $ releng-tool --version
   releng-tool <version>

opensuse
++++++++

.. code-block:: shell

   $ pip install releng-tool
   $ releng-tool --version
   releng-tool <version>

ubuntu
++++++

.. code-block:: shell

   $ sudo apt-get update
   $ sudo apt-get install python-pip
   $ sudo pip install releng-tool
   $ releng-tool --version
   releng-tool <version>

os x
~~~~

From a terminal, invoke the following commands:

.. code-block:: shell

   $ sudo easy_install pip
   $ sudo pip install releng-tool
   $ releng-tool --version
   releng-tool <version>

windows
~~~~~~~

If not already installed, download the most recent version of Python_:

   | Python - Downloads
   | https://www.python.org/downloads/

When invoking the installer, it is recommended to select the option to "Add
Python to PATH"; however, users can explicitly invoked Python from an absolute
path (the remainder of these steps will assume Python is available in the path).

Open a Windows command prompt and invoke the following:

.. code-block:: shell

   > python -m pip install releng-tool
   > python -m releng_tool --version
   releng-tool <version>

development
-----------

To install the most recent development sources, the following pip_ command can
be used:

.. code-block:: shell

   pip install git+https://github.com/releng-tool/releng-tool.git

.. _Python: https://www.python.org/
.. _pip: https://pip.pypa.io/
