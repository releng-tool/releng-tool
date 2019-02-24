user guide
==========

The following will outline the capabilities on using releng-tool with an already
defined project. For details on building a releng-tool project, consult the
:doc:`developer's guide <developer-guide>`.

getting started
---------------

Depending on the host and how releng-tool has been :doc:`installed <install>`,
the tool can be either executed using the call ``releng-tool`` (if supported) or
explicitly through a Python invoke ``python -m releng``. This guide will assume
the former option is available for use. If the alias command is not available on
the host system, the latter call can be used instead.

A releng-tool project will be defined by a ``releng.py`` configuration file
along with one or more packages found inside a ``package/`` folder. This
location can be referred to as the "root directory". When invoking
``releng-tool``, the tool will look into the current working directory for the
project information to process. For example, if a project found inside
``my-project`` with the single package ``package-a`` defined, the following
output may be observed:

.. code-block:: shell

   $ cd my-project
   $ releng-tool
   extracting package-a...
   patching package-a...
   configuring package-a...
   building package-a...
   installing package-a...
   generating license information...
   (success) completed (0:01:30)

On a successful execution, it is common that the release engineering process
will have an asset (or multiple) generated into a ``images/`` location; however,
it is up to the developer of a releng-tool project to decide where generated
files will be stored.

If a user wishes to pass the directory of a project location via command line,
the argument ``--root-dir`` can be used:

.. code-block:: shell

   $ releng-tool --root-dir my-project/
   ...

For a complete list of actions and other argument options provided by the tool,
the ``--help`` option can be used to show this information:

.. code-block:: shell

   $ releng-tool --help

arguments
---------

The command line can be used to specify either a single action to perform and/or
provide various options to configure the release engineering process. Options
can be provided before or after an action (if provided). By default, if a user
does not specify an action, it is assumed that all release engineering steps are
to be performed. An example of a user invoking a clean action is as follows:

.. code-block:: shell

   $ releng-tool clean

The following outlines available actions:

+-----------------------+------------------------------------------------------+
| ``clean``             | Clean (remove) the ``output/`` directory found in    |
|                       | the root directory. This clean operation will remove |
|                       | content such as extracted archives, built libraries  |
|                       | and more. Downloaded assets/cache files are not      |
|                       | removed (instead see ``mrproper``). If an output     |
|                       | directory is provided (i.e. ``--out-dir <dir>``)     |
|                       | during a clean event, the provided directory will be |
|                       | removed instead of the output directory (if any)     |
|                       | found in the root directory. If no output directory  |
|                       | exists, this call will have no effect.               |
+-----------------------+------------------------------------------------------+
| ``extract``           | The release engineering process will process all     |
|                       | packages up to the extraction phase (inclusive).     |
+-----------------------+------------------------------------------------------+
| ``fetch``             | The release engineering process will process all     |
|                       | packages up to the fetch phase (inclusive; see also  |
|                       | `offline builds`_).                                  |
+-----------------------+------------------------------------------------------+
| ``licenses``          | A request to generate all license information for    |
|                       | the project. Note that license information requires  |
|                       | acquiring license documents from packages.           |
|                       | Therefore, packages will be fetched/extracted if not |
|                       | already done.                                        |
+-----------------------+------------------------------------------------------+
| ``mrproper``          | Perform a pristine clean of the releng-tool project. |
|                       | This request not only removes the targeted output    |
|                       | directory but also any cached assets and mode file   |
|                       | flags (see also ``clean``).                          |
+-----------------------+------------------------------------------------------+
| ``patch``             | The release engineering process will process all     |
|                       | packages up to the patch phase (inclusive).          |
+-----------------------+------------------------------------------------------+
| ``<pkg>-build``       | Performs the build stage for the package. On         |
|                       | success, the specified package stage will have       |
|                       | completed its build. If a package has any package    |
|                       | dependencies, these dependencies will be processed   |
|                       | before the specified package. If the provided        |
|                       | package name does not exist, a notification will be  |
|                       | generated.                                           |
+-----------------------+------------------------------------------------------+
| ``<pkg>-clean``       | Cleans the build directory for package (if it        |
|                       | exists).                                             |
+-----------------------+------------------------------------------------------+
| ``<pkg>-configure``   | Performs the configure stage for the package. On     |
|                       | success, the specified package stage will have       |
|                       | completed its configuration stage. If a package has  |
|                       | any package dependencies, these dependencies will be |
|                       | processed before the specified package. If the       |
|                       | provided package name does not exist, a              |
|                       | notification will be generated.                      |
+-----------------------+------------------------------------------------------+
| ``<pkg>-extract``     | Performs the extraction stage for the package. On    |
|                       | success, the specified package stage will have       |
|                       | completed its extraction stage. If the provided      |
|                       | package name does not exist, a notification will be  |
|                       | generated.                                           |
+-----------------------+------------------------------------------------------+
| ``<pkg>-fetch``       | Performs the fetch stage for the package. On         |
|                       | success, the specified package stage will have       |
|                       | completed its fetch stage. If the provided package   |
|                       | name does not exist, a notification will be          |
|                       | generated.                                           |
+-----------------------+------------------------------------------------------+
| ``<pkg>-install``     | Performs the installation stage for the package. On  |
|                       | success, the specified package stage will have       |
|                       | completed its installation stage. If a package has   |
|                       | any package dependencies, these dependencies will be |
|                       | processed before the specified package. If the       |
|                       | provided package name does not exist, a notification |
|                       | will be generated.                                   |
+-----------------------+------------------------------------------------------+
| ``<pkg>-patch``       | Performs the patch stage for the package. On         |
|                       | success, the specified package stage will have       |
|                       | completed its patch stage. If the provided package   |
|                       | name does not exist, a notification will be          |
|                       | generated.                                           |
+-----------------------+------------------------------------------------------+
| ``<pkg>-rebuild``     | Force a rebuild of a specific package. Once a        |
|                       | package has been built, the package will not attempt |
|                       | to be built again. Invoking a rebuild request will   |
|                       | tell releng-tool to re-invoke the build step again.  |
|                       | This can be useful during times of development where |
|                       | a developer attempts to change a package definition  |
|                       | or sources between build attempts. If using this     |
|                       | action, please ensure `understanding rebuilds`_ has  |
|                       | been read to understand this action's effect.        |
+-----------------------+------------------------------------------------------+
| ``<pkg>-reconfigure`` | Force a re-configuration of a specific package. Once |
|                       | a package has been configured, the package will not  |
|                       | attempt to configure it again. Invoking a            |
|                       | re-configuration request will tell releng-tool to    |
|                       | re-invoke the configuration step again. This can be  |
|                       | useful during times of development where a developer |
|                       | attempts to change a package definition or sources   |
|                       | between configuration attempts. If using this        |
|                       | action, please ensure `understanding rebuilds`_ has  |
|                       | been read to understand this action's effect.        |
+-----------------------+------------------------------------------------------+
| ``<pkg>-reinstall``   | Force a re-installation of a specific package. Once  |
|                       | a package has been installed, the package will not   |
|                       | attempt to install it again. Invoking a              |
|                       | re-installation request will tell releng-tool to     |
|                       | re-invoke the installation step again. This can be   |
|                       | useful during times of development where a developer |
|                       | attempts to change a package definition or sources   |
|                       | between installation attempts. If using this action, |
|                       | please ensure `understanding rebuilds`_ has been     |
|                       | read to understand this action's effect.             |
+-----------------------+------------------------------------------------------+

The following outlines available options:

+---------------------------+--------------------------------------------------+
| ``--cache-dir <dir>``     | Directory for distributed version control cache  |
|                           | information (defaults to ``<root>/cache``).      |
+---------------------------+--------------------------------------------------+
| ``--debug``               | Show debug-related messages.                     |
+---------------------------+--------------------------------------------------+
| ``-D``, ``--development`` | Enables `development mode`_.                     |
+---------------------------+--------------------------------------------------+
| ``--dl-dir <dir>``        | Directory for download archives (defaults to     |
|                           | ``<root>/dl``).                                  |
+---------------------------+--------------------------------------------------+
| ``-h``, ``--help``        | Show this help.                                  |
+---------------------------+--------------------------------------------------+
| ``-j``, ``--jobs <jobs>`` | Numbers of jobs to handle (default to ``0``;     |
|                           | automatic).                                      |
+---------------------------+--------------------------------------------------+
| ``--local-sources``       | Enables `local-sources mode`_.                   |
+---------------------------+--------------------------------------------------+
| ``--nocolorout``          | Explicitly disable colorized output.             |
+---------------------------+--------------------------------------------------+
| ``--out-dir <dir>``       | Directory for output (builds, images, etc.;      |
|                           | defaults to ``<root>/output``).                  |
+---------------------------+--------------------------------------------------+
| ``--root-dir <dir>``      | Directory to process a releng-tool project       |
|                           | (defaults to the working directory).             |
+---------------------------+--------------------------------------------------+
| ``-V``, ``--verbose``     | Show additional messages.                        |
+---------------------------+--------------------------------------------------+
| ``--version``             | Show releng-tool's version.                      |
+---------------------------+--------------------------------------------------+

understanding rebuilds
----------------------

As packages are processed in order (based off of detected dependencies, if any),
each package will go through their respective stages: fetching, extraction,
patching, configuration, building and installation. While a package may not take
advantage of each stage, the releng-tool will step through each stage to track
its progress. Due to the vast number of ways a package can be defined, the
ability for releng-tool to determine when a previously executed stage is "stale"
is non-trivial. Instead of attempting to manage "stale" package stages,
releng-tool leaves the responsibility to the builder to deal with these
scenarios. This idea is important for developers to understand how it is
possible to perform rebuilds of packages to avoid a full rebuild of the entire
project.

Consider the following example: a project has three packages ``module-a``,
``module-b`` and ``module-c`` which are C++-based. For this example, project
``module-b`` depends on ``module-a`` and project ``module-c`` depends on
``module-b``; therefore, releng-tool will process packages in the order
``module-a -> module-b-> module-c``. In this example, the project is building
until a failure is detected in package ``module-c``:

.. code-block:: shell

   $ releng-tool
   [module-a built]
   [module-b built]
   [error in module-c]

A developer notices that it is due to an issue found in ``module-b``; however,
instead of attempting to redo everything from a fresh start, the developer
wishes to test the process by manually making the change in ``module-b`` to
complete the build process. The developer makes the change, re-invokes
``releng-tool`` but still notices the build error occurs:

.. code-block:: shell

   $ releng-tool
   [error in module-c]

The issue here is that since ``module-b`` has already been processed, none of
the interim changes made will be available for ``module-c`` to use. To take
advantage of the new implementation in ``module-b``, the builder can signal for
the updated package to be rebuilt:

.. code-block:: shell

   $ releng-tool module-b-rebuild
   [module-b rebuilt]

With ``module-b`` in a more desired state, a re-invoke of ``releng-tool`` could
allow ``module-c`` to be built.

.. code-block:: shell

   $ releng-tool
   [module-c built]

This is a very simple example to consider, and attempts to rebuild can vary
based on the packages, changes and languages used.

tips
----

offline builds
~~~~~~~~~~~~~~

A user can prepare for an offline build by using the ``fetch`` action:

.. code-block:: shell

   $ releng-tool fetch

Package content will be downloaded into the respective ``dl/`` and/or ``cache/``
folders. Future builds for the project will no longer need external access until
these folders are manually removed or ``mrproper`` is invoked.

parallel builds
~~~~~~~~~~~~~~~

A stage (such as a build stage) for a package can take advantage of multiple
cores to perform the step. By default, releng-tool will attempt to run as many
jobs for a stage equal to the amount of physical cores on the host system. The
amount of jobs available for a stage can be configured using the ``--jobs``
argument. For example, if a user wishes to override the amount of jobs attempted
for stages to two jobs, the following can be used:

.. code-block:: shell

   $ releng-tool --jobs 2

Note that a developer may restrict the amount of jobs allowed for a specific
package if a package cannot support parallel processing.

privileged builds
~~~~~~~~~~~~~~~~~

It is never recommended to invoke a build with elevated (e.g. root) privileges.
A builder invoking in an elevated environment runs the risk of a mis-configured
releng-tool project dirtying or destroying the builder's host environment.

license generation
~~~~~~~~~~~~~~~~~~

At the end of a ``releng-tool`` invoke, the final stages will compile a list of
package license information (if licenses are defined). If a user wishes to
compile a project's list of license information without performing an entire
build, the ``licenses`` action can be used:

.. code-block:: shell

   $ releng-tool licenses

License information can then be found in the root directory's
``<root>/licenses`` folder.

advanced builder capabilities
-----------------------------

.. _development mode:

development mode
~~~~~~~~~~~~~~~~

Development mode provides a way for builder to request to process supported
packages against a development version of sources rather than using fixed
versions. Consider the following example: if a project has a package which
sources are pulled from a Git repository, it is most likely the package
definition will define the explicit tag to clone from (e.g. ``v1.0``). However,
a package may define that the ``master`` branch of a repository is used for the
most recent development revision. If an environment is configured for
development mode, the releng-tool process will instead pull sources from the
``master`` branch instead of a release tag.

To enable development mode, invoking ``releng-tool`` with the ``--development``
argument will enable the mode. Future calls to releng-tool for the project will
use the development revision for packages where define. For example:

.. code-block:: shell

   $ releng-tool --development
   (success) configured root for development mode
   $ releng-tool
   ~building against development sources~
   ...

Development mode is persisted through the use of a file flag in the root
directory. A user can either disable development mode by performing a
``mrproper`` or can manually remove the file flag.

.. _local-sources mode:

local-sources mode
~~~~~~~~~~~~~~~~~~

.. note::

   Clean events (such as ``releng-tool clean``) will not touch packages using
   sources found alongside the output directory

Local-sources mode provides a way for a developer to build internal-flagged
packages using sources found alongside the root directory instead of having
releng-tool attempt to fetch them from remote instances. This is primarily for
developers who desire to manually manage source content outside the releng-tool
environment. Local-sources mode only works for internally flagged packaged.
Consider the following example: a releng-tool project has a package called
``liba``. When releng-tool is invoked in normal configurations, the package will
do fetching, extraction and patching to prepare the directory
``<root>/output/build/liba-<version>``. However, if a builder has configured the
working root for local-sources mode, sources for ``liba`` will be checked at the
folder ``<root>/../liba`` instead. Also, when in local-sources mode, an internal
package will skip the fetching, extraction and patching stages in order to
prevent undesired manipulation of developer-prepared sources. Another
consideration to note is the use of clean operators while in local-sources mode.
Continuing with the above example, if a user invokes ``releng-tool liba-clean``,
the operation will not remove the ``<root>/../liba`` folder. Responsibility to
managing a clean ``liba`` package will be left with the user.

To enable local-sources mode, invoking ``releng-tool`` with the
``--local-sources`` argument will enable the mode. Future calls to releng-tool
for the project will use local sources for packages defined as internal
packages. For example:

.. code-block:: shell

   $ releng-tool --local-sources
   (success) configured root for local-sources mode
   $ releng-tool
   ~building against local sources~
   ...

Local-sources mode is persisted through the use of a file flag in the root
directory. A user can either disable local sources mode by performing a
``mrproper`` or can manually remove the file flag.

.. _conf_overrides:

configuration overrides
~~~~~~~~~~~~~~~~~~~~~~~

While it is not recommended to have users manually modify a project's
configuration, a series of override options exist to deal with unique build
scenarios. If a builder needs to override a tool location or package site, a
user and define either environment options or setup a configuration override
script ``releng-overrides.py``. It is never recommended to persist a
configuration overrides file into a project's source repository.

extraction tool overrides
^^^^^^^^^^^^^^^^^^^^^^^^^

The ``override_extract_tools`` option inside a configuration override script
allows a dictionary to be provided to map an extension type to an external tool
to indicate which tool should be used for extraction. For example, when a
``.zip`` archive is being processed for extraction, releng-tool will internally
extract the archive; however, a user may wish to override this tool with their
own extraction utility. Consider the following example:

.. code-block:: python

   override_extract_tools = {
       'zip': '/opt/my-custom-unzip',
   }

revision overrides
^^^^^^^^^^^^^^^^^^

The ``override_revisions`` option inside a configuration override script allows
a dictionary to be provided to map a package name to a new revision value.
Consider the following example: a project defines ``module-a`` and ``module-b``
packages with package ``module-b`` depending on package ``module-a``. A
developer may be attempting to tweak package ``module-b`` on the fly to test a
new capabilities against the current stable version of ``module-a``; however,
the developer does not want to explicitly change the revision inside package
``module-b``'s definition. To avoid this, an override can be used instead:

.. code-block:: python

   override_revisions = {
       'module-b': '<test-branch>',
   }

The above example shows that package ``module-b`` will fetch using a test branch
instead of what is defined in the actual package definition.

site overrides
^^^^^^^^^^^^^^

The ``override_sites`` option inside a configuration override script allows a
dictionary to be provided to map a package name to a new site value. There may
be times where a host may not have access to a specific package site. To have a
host to use a mirror location without having to adjust the package definition,
the site override option can be used. For example, consider a package pulls from
site ``git@example.com:myproject.git``; however, the host ``example.com`` cannot
be access from the host machine. If a mirror location has been setup at
``git@example.org:myproject.git``, the following override can be used:

.. code-block:: python

   override_sites = {
       '<package-name>': 'git@example.org:myproject.git',
   }

tool overrides
^^^^^^^^^^^^^^

Environment variables can be used to help override external tool invoked by the
releng-tool process. For example, when invoking CMake-based projects, the tool
``cmake`` will be invoked; however, if a builder is running on CentOS and CMake
v3.x is desired, the tool ``cmake3`` needs to be invoked instead. To configure
this, an environment variable can be set to switch which tool to invoke.
Consider the following example:

.. code-block:: shell

   $ export RELENG_CMAKE=cmake3
   $ releng-tool
   [cmake3 will be used for cmake projects]

quirks
^^^^^^

releng-tool also provides a series of configuration quirks to deal with rare
host environment scenarios where releng-tool may be experiencing issues. See
:ref:`configuration quirks <quirks>` for more information.
