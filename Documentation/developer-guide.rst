developer guide
===============

The following will outline details on how to prepare a releng-tool project to be
used to assist the release engineering of a project. For details on a user
interaction with releng-tool, consult the :doc:`user's guide <user-guide>`.

prelude
-------

A releng-tool project can define multiple packages, each can be based off of
different languages, configured to use custom toolchains and more. Every package
has multiple stages (such as fetching, configuring, building, etc.) which can
help contribute to target sysroot. Once all packages are processed, the target
sysroot can be packaged for distribution.

The following outlines the (default) common directory/file locations for a
releng-tool project:

- ``cache/`` - cached content from select package sources (e.g. dvcs, etc.)
- ``dl/`` - archives for select package sources (e.g. ``.tgz``, ``.zip``, etc.)
- ``package/`` - container for packages
- ``package/<package>/`` - a package-specific folder
- ``package/<package>/<package>`` - a package definition
- ``output/`` - container for all output content
- ``output/build/`` - container for package building
- ``output/host/`` - area to hold host-specific content
- ``output/images/`` - container for final images/archives
- ``output/staging/`` - area to hold staged sysroot content
- ``output/target/`` - area to hold target sysroot content
- ``releng.py`` - project configuration

How these directories and files are used can vary on how a developer defines a
releng-tool project. Consider the following example:

1. releng-tool will load the project's configuration and respective package
   definitions to determine what steps need to be performed.
2. Package sources can be downloaded into either the ``cache/`` or ``dl/``
   folder, depending on what type of sources will be fetched. For example, Git
   sources will be stored inside of the ``cache/`` to take advantage of its
   distributable nature, and archive files (such as ``.tgz``, ``.zip``, etc.)
   will be stored inside the ``dl/`` directory.
3. Each package will be extracted into its own output directory inside
   ``output/build/``. The working areas for packages allow a package to be
   patched, configured and built based on how the developer configures the
   respective packages.
4. Once packages are built, their final executables, libraries, etc. can be
   installed into either the host area (``output/host/``), staging area
   (``output/staging/``) or the target area (``output/target/``) depending on
   what has been built. The target area is designed for the final set of assets
   produced from a build; the intent is that the files contained inside this
   folder are planned to be used on a target system (stripped, cross-compiled,
   etc.). A staging area is like a target area but may contain more content such
   as headers not intended for a final target, interim development assets, and
   more. Host content is designed for content built for the host system which
   other packages may depend on.
5. At the end of the releng-tool process, a post-stage script can be invoked to
   help archive/package content from the target area (``output/target/``) into
   the images folder (``output/images/``). For example, generating an archive
   ``output/images/my-awesome-project-v1.0.0.tgz``.

Not all projects may use each of these folders or take advantage of each stage.
While various capabilities exist, it does not mean releng-tool will handle all
the nitty-gritty details to make a proper build of a project. For example:

- If a developer wishes to cross-compile a package to a target, they must ensure
  the package is configured in the proper manner to use a desired toolchain.
- If a developer wants to process a Python package, they must ensure the proper
  interpreter is used if they cannot rely on the host's default interpreter.
- If a developer develops script-based packages, they must ensure that these
  scripts properly handle multiple re-invokes (e.g. if a builder performs a
  rebuild on a package).

releng-tool will attempt to provide an easy way to deal with fetching sources,
ensuring projects are invoked in order, and more; however, the more advanced
features/actions a developer may want in their release engineering (like the
examples above), the more a developer will need to manage in their project.

getting started
---------------

releng-tool is made on Python. This document will outline package definitions,
scripts and more which are most likely Python scripts, and in turn will be
invoked/processed by the releng-tool. While releng-tool supports running on
various host systems (e.g. Linux, OS X, Windows, etc.), this guide will
primarily show examples following a Unix-styled file system.

The following will provide a very simple script-based project solution to get
started. This example will make a project with two packages, setup a dependency
between them and setup scripts to help show a developer how packages are
processed. If there is no desire to make a simple project example, one may
venture to the `actually getting started`_ section.

To start, make a new folder for the project, two sample packages and move into
the root folder:

.. code-block:: shell

   $ mkdir -p my-project/package/libx
   $ mkdir -p my-project/package/liby
   $ cd my-project/

Inside the ``libx`` project, the package definition and script-based files will
be created. First, build the package definition ``my-project/libx/libx`` with
the following content:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   LIBX_VERSION='1.0.0'

Next, create a build script for the ``libx`` project ``my-project/libx/build``
with the following content:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   print('invoked libx package build stage')

This is a very simple script-based package (all package options explained later
in this document). Repeat the same steps for the ``liby`` package with the file
``my-project/liby/liby`` containing:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   LIBY_DEPENDENCIES=['libx']
   LIBY_VERSION='2.1.0'

And ``my-project/liby/build`` containing:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   print('invoked liby package build stage')

One difference with this package is the definition of ``LIBY_DEPENDENCIES``,
which tells releng-tool to ensure that ``libx`` package is processed before
``liby``.

With this minimal set of packages, the project's releng-tool configuration can
now be created. At the root of the project folder, create a ``releng.py``
configuration file with the following contents:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   packages = [
       'libx',
       'liby',
   ]

This sample project should be ready for a spin. While in the ``my-project``
folder, invoke ``releng-tool``:

.. code-block:: shell

   $ releng-tool
   patching libx...
   configuring libx...
   building libx...
   invoked libx package build stage
   installing libx...
   patching liby...
   configuring liby...
   building liby...
   invoked liby package build stage
   installing liby...
   generating license information...
   (success) completed (0:00:00)

This above output shows that the ``libx`` package's stage are invoke followed by
``liby`` package's stages. For the build stage in each package, each respective
package script has been invoked. While this example only prints a message, more
elaborate scripts can be made to handle a package's source to build.

To clean the project, a ``releng-tool clean`` request can be invoked:

.. code-block:: shell

   $ releng-tool clean

Now the project is in a state again to perform a fresh build. This concludes the
initial getting started example. Feel free to remove the example project and
prepare for steps to make a real releng-tool project.

actually getting started
------------------------

Start building a new releng-tool project by creating the following root and
package folders for a project, and venture into the root folder:

.. code-block:: shell

   $ mkdir -p <my-project>/package
   $ cd <my-project>/

Inside the root folder, create a releng-tool configuration file ``releng.py``
with the following skeleton content:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   packages = [
   ]

This configuration defines a releng-tool project with no packages. Start to
change this by adding a package or more for each a module to be built in the
release engineering process. For example, packages can be individual static
libraries, simple asset fetching (e.g. image/document downloading) and more.

For each package, create a new folder inside ``<my-project>/package`` to
represent the package.

.. code-block:: shell

   $ mkdir <my-project>/package/<my-package>

Inside each newly created package, create a package definition file. This
(Python-based) file will be named with the same name as the package folder (i.e.
``<my-project>/package/<my-package>/<my-package>``). An initial skeleton
structure for the definition file is as follows:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   MY_PACKAGE_DEPENDENCIES=[]
   MY_PACKAGE_LICENSE=['<license name>']
   MY_PACKAGE_LICENSE_FILES=['<license file>']
   MY_PACKAGE_SITE='<location for sources>'
   MY_PACKAGE_TYPE='<package-type>'
   MY_PACKAGE_VERSION='<package-version>'

Initial changes to note:

- For a package, any support package variable requires the package name as a
  prefix. The prefix should be a underscore-separated all-uppercase string
  value. In the above example, if the package name was ``my-package``, the
  prefix will be ``MY_PACKAGE_``.
- One of the most important options is the version option
  (``MY_PACKAGE_VERSION``). This value is used to help manage downloaded asset
  names, build output directories and sometimes even revision values for
  source-fetching. An example of a good version value is '1.0'; however, the
  value can vary depending on the package being defined.
- The site value (``MY_PACKAGE_SITE``) is used to identify where source/assets
  can be fetched from. A site can be a Git repository, a URL, SCP location, a
  site value supported by a custom fetch extension or more.
- A helpful configuration option is the dependency list
  (``MY_PACKAGE_DEPENDENCIES``). If a package depends on another package being
  built, the name of the package should be listed in this option. This ensures
  that releng-tool will invoke package stages in the appropriate order.
- While not required, it is recommended to provide license tracking for packages
  when possible. ``MY_PACKAGE_LICENSE`` and ``MY_PACKAGE_LICENSE_FILES`` are
  list values to define the list of licenses applicable to this package and the
  location of the respective license files found in the sources. A developer can
  exclude these options if desired. If a developer does provide these options,
  the end of the build process will compile a document of used licenses for the
  project.
- The type of package (``MY_PACKAGE_TYPE``) can be used to take advantage of
  various package types supported by releng-tool. By default, packages are
  script-based, where Python scripts inside the packages are invoked during each
  stage (e.g. ``<my-project>/package/build`` would be invoked during the build
  phase). releng-tool also supports other package types such as autotools, CMake
  and more to limit the need to define custom scripts for common build steps.
  Developers can also use package types defined by included extensions (if any).

A detailed list of options can be found in `common package configurations`_ and
`advanced package configurations`_.

Once all packages have been prepared with desired package definitions options,
the root configuration script (``releng.py``) should be updated to indicate
which packages should be built. All packages can be defined in the ``packages``
list if desired. For example, if a project has packages ``liba``, ``libb`` and
``programc``, the following package list can be defined:

.. code-block:: python

   packages = [
       'liba',
       'libb',
       'programc',
   ]

Note that a developer does not need to explicitly add each component if
dependencies are configured. Considering the same packages listed above, if
``programc`` depends on both ``liba`` and ``libb`` packages, only ``programc``
needs to be explicitly listed:

.. code-block:: python

   packages = [
       'programc',
   ]

When processing, both ``liba`` and ``libb`` packages will be implicitly loaded
and processed like any other package.

Once all the project's packages are ready, a developer can try their luck by
attempting to perform the release engineering process:

.. code-block:: shell

   $ releng-tool

A developer may not have luck on the first go. Tweaks may be needed on the
package definitions, custom scripts (if used) and issues found in sources. A
developer may invoke ``releng-tool`` multiple times to attempt to continue the
build process for a project. A developer may wish to use the ``clean`` option to
remove an existing extracted sources/partially built sources:

.. code-block:: shell

   $ releng-tool clean

Or start from a completely fresh state using ``mrproper`` to remove any
downloaded/cached resources:

.. code-block:: shell

   $ releng-tool mrproper

There may also be times if a single project needs to be cleaned:

.. code-block:: shell

   $ releng-tool my-package-clean

Consult the :doc:`user's guide <user-guide>` for more action information.

Eventually the project should be in a good state that each package is being
built as expected. Now a user can decide on what to do with the resulting files.
After the invoke of a releng-tool process, it is typical for final binaries,
public includes, etc. to be found inside the ``<root>/output/target`` directory.
If a developer only desires to manually take the assets from this folder and
distribute/store them, no additional steps are required. However, it may be
common that a developer wants to package some assets (whether it be a
tar/zip/etc. container, pkg/rpm/etc. package or more). A developer could deal
with such a capability outside the releng-tool process; but if a developer
wishes to hook the end of the process, a post-processing script can be used.

A developer may create a post-processing file ``post.py`` in the root directory.
On the completion of processing each package, the post-processing script will be
invoked. It is important to note that the post-processing script may be invoked
multiple times if a user attempts to rebuild the project. For example, if the
file ``post.py`` has the following contents:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   print('project target directory: {}'.format(TARGET_DIR))

The target directory will be output to standard out at the end of the build. A
developer may wish to define their own Python script to decide on how to package
the contents found in ``TARGET_DIR`` (see also `script helpers`_ for helper
variables/functions).

releng.py
---------

A releng-tool project defines its configuration options inside the a
``releng.py`` file at the root of a project. The primary configuration option
for a developer to define is ``packages``, which is used to hold a list of
packages to be processed:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   packages = [
       'package-a',
       'package-b',
       'package-c',
   ]

A series of additional configuration options are available to be defined inside
the project's configuration. A list of common configuration options are as
follows:

+--------------------------+---------------------------------------------------+
| .. _CONF_DEFAULT_INTERN: |                                                   |
|                          |                                                   |
| ``default_internal``     | A flag to indicate that projects are implicitly   |
|                          | loaded as internal projects. By default, packages |
|                          | not explicitly configured as internal or external |
|                          | are assumed to be external packages.              |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    default_internal = True                        |
|                          |                                                   |
|                          | See also `internal and external packages`_.       |
+--------------------------+---------------------------------------------------+
| ``extensions``           | A list of extensions to load before processing a  |
|                          | releng-tool project. If an extension cannot be    |
|                          | loaded, the release engineering process will fail |
|                          | with detailed information.                        |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    extensions = [                                 |
|                          |        'ext-a',                                   |
|                          |        'ext-b',                                   |
|                          |    ]                                              |
|                          |                                                   |
|                          | See also `loading extensions`_.                   |
+--------------------------+---------------------------------------------------+
| ``external_packages``    | A list of external package locations. By default, |
|                          | packages for a project will be searched for in    |
|                          | root directory's package folder                   |
|                          | (``<root>/package``). In some build environments, |
|                          | some packages may be required or may be preferred |
|                          | to be located in another location/repository. To  |
|                          | allow packages to be loaded from another package  |
|                          | container directory, one or more package          |
|                          | locations can be provided. For example:           |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    external_packages = [                          |
|                          |        os.environ['MY_EXTERNAL_PKG_DIR'],         |
|                          |    ]                                              |
+--------------------------+---------------------------------------------------+
| .. _CONF_LICENSE_HEADER: |                                                   |
|                          |                                                   |
| ``license_header``       | As the releng-tool build process is finalized,    |
|                          | a license document can be generated containing    |
|                          | each package's license information. If a          |
|                          | developer wishes to add a custom header to the    |
|                          | generated document, a header can be defined by    |
|                          | project's configuration. For example:             |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    license_header = 'my leading content'          |
|                          |                                                   |
|                          | See also `licenses`_.                             |
+--------------------------+---------------------------------------------------+
| ``packages``             | A list of packages to process. Packages listed    |
|                          | will be processed by releng-tool till their       |
|                          | completion. Package dependencies not explicitly   |
|                          | listed will be automatically loaded and processed |
|                          | as well.                                          |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    packages = [                                   |
|                          |        'package-a',                               |
|                          |        'package-b',                               |
|                          |        'package-c',                               |
|                          |    ]                                              |
+--------------------------+---------------------------------------------------+
| .. _CONF_SYSROOT_PREFIX: |                                                   |
|                          |                                                   |
| ``sysroot_prefix``       | Define a custom sysroot prefix to provide to      |
|                          | packages during their configuration, build and    |
|                          | installation stages. By default, the sysroot      |
|                          | prefix is set to ``/usr``.                        |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    sysroot_prefix = '/usr'                        |
|                          |                                                   |
|                          | See also |CONF_PREFIX|_.                          |
+--------------------------+---------------------------------------------------+
| ``url_mirror``           | Specifies a mirror base site to be used for URL   |
|                          | fetch requests. If this option is set, any URL    |
|                          | fetch requests will first be tried on the         |
|                          | configured mirror before attempting to acquired   |
|                          | from the defined site in a package definition.    |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    url_mirror = 'ftp://mirror.example.org/data/'  |
+--------------------------+---------------------------------------------------+

.. |CONF_DEFAULT_INTERN| replace:: ``default_internal``
.. |CONF_LICENSE_HEADER| replace:: ``license_header``
.. |CONF_SYSROOT_PREFIX| replace:: ``sysroot_prefix``

A list of more advanced configuration options are as follows:

+--------------------------+---------------------------------------------------+
| ``cache_ext``            | A transform for cache extension interpreting.     |
|                          | This is an advanced configuration and is not      |
|                          | recommended for use except for special use cases  |
|                          | outlined below.                                   |
|                          |                                                   |
|                          | When releng-tool fetches assets from remote       |
|                          | sites, the site value can used to determine the   |
|                          | resulting filename of a cached asset. For         |
|                          | example, downloading an asset from                |
|                          | ``https://example.org/my-file.tgz``, the locally  |
|                          | downloaded file will result in a ``.tgz``         |
|                          | extension; however, not all defined sites will    |
|                          | result in a easily interpreted cache extension.   |
|                          | While releng-tool will attempt its best to        |
|                          | determine an appropriate extension value to use,  |
|                          | some use cases may not be able to be handled. To  |
|                          | deal with these cases, a developer can define a   |
|                          | transform method to help translate a site value   |
|                          | into a known cache extension value.               |
|                          |                                                   |
|                          | Consider the following example: a host is used to |
|                          | acquire assets from a content server. The URI to  |
|                          | download an asset uses a unique request format    |
|                          | ``https://static.example.org/fetch/25134``.       |
|                          | releng-tool may not be able to find the extension |
|                          | for the fetched asset, but if a developer knows   |
|                          | the expected archive types for these calls, a     |
|                          | custom transform can be defined. For example:     |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    def my_translator(site):                       |
|                          |        if 'static.example.org' in site:           |
|                          |            return 'tgz'                           |
|                          |        return None                                |
|                          |                                                   |
|                          |    cache_ext = my_translator                      |
|                          |                                                   |
|                          | The above transform indicates that all packages   |
|                          | using the ``static.example.org`` site will be     |
|                          | ``tgz`` archives.                                 |
+--------------------------+---------------------------------------------------+
| ``override_revisions``   | Allows a dictionary to be provided to map a       |
|                          | package name to a new revision value. Consider    |
|                          | the following example: a project defines          |
|                          | ``module-a`` and ``module-b`` packages with       |
|                          | package ``module-b`` depending on package         |
|                          | ``module-a``. A developer may be attempting to    |
|                          | tweak package ``module-b`` on the fly to test a   |
|                          | new capabilities against the current stable       |
|                          | version of ``module-a``; however, the developer   |
|                          | does not want to explicitly change the revision   |
|                          | inside package ``module-b``'s definition. To      |
|                          | avoid this, an override can be used instead:      |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    override_revisions={                           |
|                          |        'module-b': '<test-branch>',               |
|                          |   }                                               |
|                          |                                                   |
|                          | The above example shows that package ``module-b`` |
|                          | will fetch using a test branch instead of what is |
|                          | defined in the actual package definition.         |
|                          |                                                   |
|                          | Note that the use of an override option should    |
|                          | only be used in special cases (see also           |
|                          | :ref:`configuration overrides <conf_overrides>`). |
+--------------------------+---------------------------------------------------+
| ``override_sites``       | A dictionary to be provided to map a package name |
|                          | to a new site value. There may be times where a   |
|                          | host may not have access to a specific package    |
|                          | site. To have a host to use a mirror location     |
|                          | without having to adjust the package definition,  |
|                          | the site override option can be used. For         |
|                          | example, consider a package pulls from site       |
|                          | ``git@example.com:myproject.git``; however, the   |
|                          | host ``example.com`` cannot be access from the    |
|                          | host machine. If a mirror location has been setup |
|                          | at ``git@example.org:myproject.git``, the         |
|                          | following override can be used:                   |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    override_sites={                               |
|                          |        '<pkg>': 'git@example.org:myproject.git',  |
|                          |    }                                              |
|                          |                                                   |
|                          | Note that the use of an override option should    |
|                          | only be used in special cases (see also           |
|                          | :ref:`configuration overrides <conf_overrides>`). |
+--------------------------+---------------------------------------------------+
| ``override_tools``       | A dictionary to be provided to map an external    |
|                          | tool name to a specific path. For example, when   |
|                          | invoking CMake-based projects, the tool ``cmake`` |
|                          | will be invoked; however, if a builder is running |
|                          | on CentOS and CMake v3.x is desired, the tool     |
|                          | ``cmake3`` needs to be invoked instead. This      |
|                          | override can be used to tell releng-tool to use   |
|                          | the newer version of CMake. Consider the          |
|                          | following example:                                |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    override_tools={                               |
|                          |        'cmake': 'cmake3',                         |
|                          |        'scp': '/opt/my-custom-scp-build/scp',     |
|                          |    }                                              |
|                          |                                                   |
|                          | Note that the use of an override option should    |
|                          | only be used in special cases (see also           |
|                          | :ref:`configuration overrides <conf_overrides>`). |
+--------------------------+---------------------------------------------------+

environment variables
---------------------

When packages and the post-processing event are processed, the following
environment variables will be made available:

+--------------------------+---------------------------------------------------+
| ``BUILD_DIR``            | The build directory.                              |
+--------------------------+---------------------------------------------------+
| ``CACHE_DIR``            | The cache directory.                              |
+--------------------------+---------------------------------------------------+
| ``DL_DIR``               | The download directory.                           |
+--------------------------+---------------------------------------------------+
| ``HOST_DIR``             | The host directory.                               |
+--------------------------+---------------------------------------------------+
| ``IMAGES_DIR``           | The images directory.                             |
+--------------------------+---------------------------------------------------+
| ``LICENSE_DIR``          | The licenses directory.                           |
|                          |                                                   |
|                          | See also `licenses`_.                             |
+--------------------------+---------------------------------------------------+
| .. _CONF_NJOBS:          |                                                   |
|                          |                                                   |
| ``NJOBS``                | Number of calculated jobs to allow at a given     |
|                          | time. Unless explicitly set by a system builder   |
|                          | on the command line, the calculated number of     |
|                          | jobs should be equal to the number of physical    |
|                          | cores on the host. When building a specific       |
|                          | package and the package overrides the number of   |
|                          | jobs to use, the package-defined count will be    |
|                          | used instead. This configuration will always be a |
|                          | value of at least one (1).                        |
+--------------------------+---------------------------------------------------+
| .. _CONF_NJOBSCONF:      |                                                   |
|                          |                                                   |
| ``NJOBSCONF``            | Number of jobs to allow at a given time. Unlike   |
|                          | |CONF_NJOBS|_, ``NJOBSCONF`` provides the         |
|                          | requested configured number of jobs to use. The   |
|                          | value may be set to zero (0) to indicate an       |
|                          | automatic detection of jobs to use. This can be   |
|                          | useful for tools which have their own automatic   |
|                          | job count implementation and do not want to rely  |
|                          | on the value defined by |CONF_NJOBS|_. When       |
|                          | building a specific package and the package       |
|                          | overrides the number of jobs to use, the          |
|                          | package-defined count will be used instead.       |
+--------------------------+---------------------------------------------------+
| ``OUTPUT_DIR``           | The output directory.                             |
+--------------------------+---------------------------------------------------+
| .. _CONF_PKG_BUILD_DIR:  |                                                   |
|                          |                                                   |
| ``PKG_BUILD_DIR``        | The directory for a specific package's buildable  |
|                          | content (see also |CONF_PKG_BUILD_ODIR|_).        |
+--------------------------+---------------------------------------------------+
| .. _CONF_PKG_BUILD_ODIR: |                                                   |
|                          |                                                   |
| ``PKG_BUILD_OUTPUT_DIR`` | The directory for where a package's build output  |
|                          | will be stored (see also |CONF_PKG_BUILD_DIR|_).  |
+--------------------------+---------------------------------------------------+
| ``PKG_CACHE_FILE``       | The location of the cache file for a package. If  |
|                          | package defines a fetch of an archive from a      |
|                          | remote source, after the fetch stage is           |
|                          | completed, the archive can be found in this       |
|                          | location. For example, if a package defines a     |
|                          | site ``https://www.example.com/test.tgz``, the    |
|                          | resulting catch file may be                       |
|                          | ``<root>/output/dl/test-1.0.tgz``.                |
+--------------------------+---------------------------------------------------+
| ``PKG_DEFDIR``           | The package's definition directory. For example,  |
|                          | for a package ``test``. the definition directory  |
|                          | would be ``<root>/package/test``.                 |
+--------------------------+---------------------------------------------------+
| ``PKG_INTERNAL``         | Whether or not the package is considered          |
|                          | "internal". If internal, the environment variable |
|                          | will be set to a value of one (i.e.               |
|                          | ``PKG_INTERNAL=1``).                              |
|                          |                                                   |
|                          | See also `internal and external packages`_.       |
+--------------------------+---------------------------------------------------+
| ``PKG_NAME``             | The name of the package.                          |
+--------------------------+---------------------------------------------------+
| ``PKG_SITE``             | The site of the package (see also |CONF_SITE|_).  |
+--------------------------+---------------------------------------------------+
| ``PKG_VERSION``          | The version of the package.                       |
+--------------------------+---------------------------------------------------+
| ``PREFIX``               | The sysroot prefix for the package.               |
+--------------------------+---------------------------------------------------+
| ``RELENG_REBUILD``       | Flag set if performing a re-build request.        |
+--------------------------+---------------------------------------------------+
| ``RELENG_RECONFIGURE``   | Flag set if performing a re-configuration         |
|                          | request.                                          |
+--------------------------+---------------------------------------------------+
| ``RELENG_REINSTALL``     | Flag set if performing a re-install request.      |
+--------------------------+---------------------------------------------------+
| ``ROOT_DIR``             | The root directory.                               |
+--------------------------+---------------------------------------------------+
| ``STAGING_DIR``          | The staging area directory.                       |
+--------------------------+---------------------------------------------------+
| ``SYMBOLS_DIR``          | The symbols area directory.                       |
+--------------------------+---------------------------------------------------+
| ``TARGET_DIR``           | The target area directory.                        |
+--------------------------+---------------------------------------------------+

.. |CONF_NJOBSCONF| replace:: ``NJOBSCONF``
.. |CONF_NJOBS| replace:: ``NJOBS``
.. |CONF_PKG_BUILD_DIR| replace:: ``PKG_BUILD_DIR``
.. |CONF_PKG_BUILD_ODIR| replace:: ``PKG_BUILD_OUTPUT_DIR``

Package-defined environment variables are also available in the rare chance
that package content needs to be mangled (e.g. including a dependent module
which does not properly support a sysroot staged environment). The following
package-defined environment variables are available for use (where ``<PKG>``
translates to a releng-tool's determined package key):

+----------------------------+-------------------------------------------------+
| ``<PKG>_BUILD_DIR``        | The directory for a defined package's           |
|                            | buildable content.                              |
+----------------------------+-------------------------------------------------+
| ``<PKG>_BUILD_OUTPUT_DIR`` | The directory for where a defined package's     |
|                            | build output will be stored.                    |
+----------------------------+-------------------------------------------------+
| ``<PKG>_NAME``             | The name of the package.                        |
+----------------------------+-------------------------------------------------+
| ``<PKG>_VERSION``          | The version of a defined package.               |
+----------------------------+-------------------------------------------------+

Note that is it not recommended to define environment variables for the
releng-tool process to use outside the project definition except for special
cases (such as authentication tokens, etc.). Attempting to configure, for
example, compiler flags outside the project definition circumvents configuration
control a releng-tool project aims to maintain.

packages
--------

Packages are defined inside the ``package/`` directory. There is no explicit
limit on the total number of packages a project can have. Packages can consist
of libraries, programs or even basic assets. Package names are recommended to be
lower-case with dash-separated (``-``) separators (if needed). For example,
``package-a`` is recommended over ``PackageA`` or ``package_a``; however, the
choice is up to the developer making the releng-tool project.

When making a package, a container folder for the package as well as a package
definition file needs to be made. For example, if the package is ``package-a``,
the file ``package/package-a/package-a`` should exist. Package definition files
are Python-based, thus the following leading header is recommended:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

Inside the definition file, a series of configuration options can be set to tell
releng-tool how to work with the defined package. Each option is prefixed with
a variable-safe variant of the package name. The prefix value will be an
uppercase string based on the package name with special characters converted to
underscores. For example, ``package-a`` will have a prefix ``PACKAGE_A_``. For a
package to take advantage of a configuration option, the package definition will
add a variable entry with the package's prefix followed by the
supported option name. Considering the same package with the name ``package-a``
(and prefix ``PACKAGE_A_``), to use the |CONF_VERSION|_ configuration option,
the following can be defined (``PACKAGE_A_VERSION``):

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   PACKAGE_A_VERSION='1.0.0'

More details on available configuration options are as follows.

common package configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following outlines common configuration options available for packages:

+--------------------------+---------------------------------------------------+
| ``DEPENDENCIES``         | List of package dependencies a given project has. |
|                          | If a project depends on another package, the      |
|                          | package name should be listed in this option.     |
|                          | This ensures releng-tool will process packages in |
|                          | the proper order. The following shows an example  |
|                          | package ``libc`` being dependent on ``liba`` and  |
|                          | ``libb`` being processed first:                   |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBC_DEPENDENCIES = ['liba', 'libb']           |
|                          |                                                   |
+--------------------------+---------------------------------------------------+
| ``INSTALL_TYPE``         | Defines the installation type of this package. A  |
|                          | package may be designed to be built and installed |
|                          | for just the target area, the stage area, both or |
|                          | maybe in the host directory. The following        |
|                          | options are available for the installation type:  |
|                          |                                                   |
|                          | - ``host`` - the host directory                   |
|                          | - ``images`` - the images directory               |
|                          | - ``staging`` - the staging area                  |
|                          | - ``staging_and_target`` - both the staging an    |
|                          |   target area                                     |
|                          | - ``target`` - the target area                    |
|                          |                                                   |
|                          | The default installation type is ``target``.      |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_INSTALL_TYPE = 'target'                 |
|                          |                                                   |
+--------------------------+---------------------------------------------------+
| .. _CONF_LICENSE:        |                                                   |
|                          |                                                   |
| ``LICENSE``              | A string or list of strings outlining the         |
|                          | license information for a package. Outlining the  |
|                          | license of a package is always recommended (but   |
|                          | not required).                                    |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_LICENSE = ['GPLv2', 'MIT']              |
|                          |                                                   |
|                          | or                                                |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_LICENSE = 'Proprietary'                 |
|                          |                                                   |
|                          |                                                   |
|                          | See also |CONF_LICENSE_FILES|_.                   |
+--------------------------+---------------------------------------------------+
| .. _CONF_LICENSE_FILES:  |                                                   |
|                          |                                                   |
| ``LICENSE_FILES``        | A string or list of strings identifying the       |
|                          | license files found inside the package sources    |
|                          | which match up to the defined ``LICENSE`` entries |
|                          | (respectively). Listing the license(s) of a       |
|                          | package is always recommended (but not required). |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_LICENSE_FILES = [                       |
|                          |        'LICENSE.GPLv2',                           |
|                          |        'LICENSE.MIT',                             |
|                          |    ]                                              |
|                          |                                                   |
|                          | or                                                |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_LICENSE_FILES = 'LICENSE'               |
|                          |                                                   |
|                          | See also |CONF_LICENSE|_.                         |
+--------------------------+---------------------------------------------------+
| .. _CONF_SITE:           |                                                   |
|                          |                                                   |
| ``SITE``                 | The site where package sources/assets can be      |
|                          | found. The site can be a URL of an archive, or    |
|                          | describe a source control URL such as Git or SVN. |
|                          | The following outline a series of supported site  |
|                          | definitions:                                      |
|                          |                                                   |
|                          | ========= ===                                     |
|                          | type      prefix/postfix                          |
|                          | ========= ===                                     |
|                          | Bazaar    ``bzr+``                                |
|                          | CVS       ``cvs+``                                |
|                          | Git       ``git+`` or ``.git``                    |
|                          | Mercurial ``hg+``                                 |
|                          | SCP       ``scp+``                                |
|                          | SVN       ``svn+``                                |
|                          | URL       `(wildcard)`                            |
|                          | ========= ===                                     |
|                          |                                                   |
|                          | Examples include:                                 |
|                          |                                                   |
|                          | .. parsed-literal::                               |
|                          |                                                   |
|                          |    LIBFOO_SITE = '|GITSITE_EXAMPLE|'              |
|                          |    LIBFOO_SITE = '|CVSSITE_EXAMPLE|'              |
|                          |    LIBFOO_SITE = '|SVNSITE_EXAMPLE|'              |
|                          |    LIBFOO_SITE = '|URLSITE_EXAMPLE|'              |
|                          |                                                   |
|                          | A developer can also use |CONF_VCS_TYPE|_ to      |
|                          | explicitly define the version control system type |
|                          | without the need for a prefix/postfix entry.      |
|                          |                                                   |
|                          | For more information on each type's formatting,   |
|                          | consult                                           |
|                          | :ref:`site definitions <site_definitions>`.       |
|                          |                                                   |
|                          | Using a specific type will create a dependency    |
|                          | for a project that the respective host tool is    |
|                          | installed on the host system. For example, if a   |
|                          | Git site is set, the host system will need to     |
|                          | have ``git`` installed on the system.             |
|                          |                                                   |
|                          | If no site is defined for a package, it will be   |
|                          | considered a virtual package (i.e. has no         |
|                          | content). If applicable, loaded extensions may    |
|                          | provide support for custom site protocols.        |
|                          |                                                   |
|                          | See also |CONF_VCS_TYPE|_.                        |
+--------------------------+---------------------------------------------------+
| .. _CONF_TYPE:           |                                                   |
|                          |                                                   |
| ``TYPE``                 | The package type. The default package type is a   |
|                          | (Python) script-based package; however,           |
|                          | releng-tool also provides a series of helper      |
|                          | package types for common frameworks. The          |
|                          | following outline a series of supported site      |
|                          | definitions:                                      |
|                          |                                                   |
|                          | ========= ===                                     |
|                          | type      value                                   |
|                          | ========= ===                                     |
|                          | Autotools ``autotools``                           |
|                          | CMake     ``cmake``                               |
|                          | Python    ``python``                              |
|                          | Script    ``script``                              |
|                          | ========= ===                                     |
|                          |                                                   |
|                          | If no type is defined for a package, it will be   |
|                          | considered a script-based package. If applicable, |
|                          | loaded extensions may provide support for custom  |
|                          | site protocols.                                   |
|                          |                                                   |
|                          | Using a specific type will create a dependency    |
|                          | for a project that the respective host tool is    |
|                          | installed on the host system. For example, if a   |
|                          | CMake type is set, the host system will need to   |
|                          | have ``cmake`` installed on the system.           |
+--------------------------+---------------------------------------------------+
| .. _CONF_VERSION:        |                                                   |
|                          |                                                   |
| ``VERSION``              | The version of the package. Typically the version |
|                          | value should be formatted in a semantic           |
|                          | versioning style; however, it is up to the        |
|                          | developer to decide the best version value to use |
|                          | for a package. It is important to note that the   |
|                          | version value is used to determine build output   |
|                          | folder names, cache files and more.               |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_VERSION = '1.0.0'                       |
|                          |                                                   |
|                          | For some VCS types, the version value will be     |
|                          | used to acquire a specific revision of sources.   |
|                          | If for some case the desired version value cannot |
|                          | be gracefully defined (e.g. ``libfoo-v1.0`` will  |
|                          | produce output directories such as                |
|                          | ``libfoo-libfoo-v1.0``), |CONF_REVISION|_ can be  |
|                          | used.                                             |
|                          |                                                   |
|                          | See also |CONF_DEVMODE_REV|_ and                  |
|                          | |CONF_REVISION|_.                                 |
+--------------------------+---------------------------------------------------+

.. |CONF_LICENSE| replace:: ``LICENSE``
.. |CONF_LICENSE_FILES| replace:: ``LICENSE_FILES``
.. |CONF_SITE| replace:: ``SITE``
.. |CONF_TYPE| replace:: ``TYPE``
.. |CONF_VERSION| replace:: ``VERSION``
.. |CVSSITE_EXAMPLE| replace:: cvs+:pserver:anonymous@cvs.example.com:/var/lib/cvsroot mymodule
.. |GITSITE_EXAMPLE| replace:: \https://example.com/libfoo.git
.. |SVNSITE_EXAMPLE| replace:: svn+\https://svn.example.com/repos/libfoo/c/branches/libfoo-1.2
.. |URLSITE_EXAMPLE| replace:: \https://www.example.com/files/libfoo.tar.gz

advanced package configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following outlines more advanced configuration options available for
packages:

+--------------------------+---------------------------------------------------+
| ``BUILD_SUBDIR``         | Sub-directory where a package's extracted sources |
|                          | holds its buildable content. Sources for a        |
|                          | package may be nested inside one or more          |
|                          | directories. A package can specify the            |
|                          | sub-directory where the configuration, build and  |
|                          | installation processes are invoked from.          |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_BUILD_SUBDIR = 'subdir'                 |
|                          |                                                   |
+--------------------------+---------------------------------------------------+
| .. _CONF_DEVMODE_REV:    |                                                   |
|                          |                                                   |
| ``DEVMODE_REVISION``     | Specifies a development revision for a package.   |
|                          | When a project is being built in                  |
|                          | :ref:`development mode`, the development revision |
|                          | is used over the configured |CONF_REVISION|_      |
|                          | value. If a development revision is not defined   |
|                          | for a project, a package will still use the       |
|                          | configured |CONF_REVISION|_ while in development  |
|                          | mode.                                             |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_DEVMODE_REVISION = 'feature/alpha'      |
|                          |                                                   |
|                          | See also |CONF_REVISION|_ and |CONF_VERSION|_.    |
+--------------------------+---------------------------------------------------+
| ``EXTENSION``            | Specifies a filename extension for the package.   |
|                          | A package may be cached inside the download       |
|                          | directory to be used when the extraction phase is |
|                          | invoked. releng-tool attempts to determine the    |
|                          | most ideal extension for this cache file; however |
|                          | some cases the detected extension may be          |
|                          | incorrect. To deal with this situation, a         |
|                          | developer can explicitly specify the extension    |
|                          | value using this option.                          |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_EXTENSION = 'tgz'                       |
|                          |                                                   |
+--------------------------+---------------------------------------------------+
| .. _CONF_EXTERNAL:       |                                                   |
|                          |                                                   |
| ``EXTERNAL``             | Flag value to explicitly indicate that a package  |
|                          | is an external package. External packages will    |
|                          | generate warnings if :ref:`hashes <hash_files>`   |
|                          | or `licenses`_ are missing. By default, packages  |
|                          | are considered external unless explicitly         |
|                          | configured to be internal.                        |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_EXTERNAL = True                         |
|                          |                                                   |
|                          | See also `internal and external packages`_.       |
+--------------------------+---------------------------------------------------+
| ``EXTOPT``               | Specifies extension-specific options. Packages    |
|                          | wishing to take advantage of extension-specific   |
|                          | capabilities can forward options to extensions by |
|                          | defining a dictionary of values.                  |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_EXTOPT = {                              |
|                          |        'option-a': True,                          |
|                          |        'option-b': 'value',                       |
|                          |    }                                              |
|                          |                                                   |
+--------------------------+---------------------------------------------------+
| ``EXTRACT_TYPE``         | Specifies a custom extraction type for a package. |
|                          | If a configured extension supports a custom       |
|                          | extraction capability, the registered extraction  |
|                          | type can be explicitly registered in this option. |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_EXTRACT_TYPE = 'ext-custom-extract'     |
|                          |                                                   |
+--------------------------+---------------------------------------------------+
| ``FIXED_JOBS``           | Explicitly configure the total number of jobs a   |
|                          | package can use. The primary use case for this    |
|                          | option is to help limit the total number of jobs  |
|                          | for a package that cannot support a large or any  |
|                          | parallel build environment.                       |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_FIXED_JOBS = 1                          |
|                          |                                                   |
+--------------------------+---------------------------------------------------+
| .. _CONF_INTERNAL:       |                                                   |
|                          |                                                   |
| ``INTERNAL``             | Flag value to explicitly indicate that a package  |
|                          | is an internal package. Internal packages will    |
|                          | not generate warnings if                          |
|                          | :ref:`hashes <hash_files>` or `licenses`_ are     |
|                          | missing. When configured in                       |
|                          | :ref:`local-sources mode`, package sources are    |
|                          | searched for in the local directory opposed to    |
|                          | site fetched sources. By default, packages are    |
|                          | considered external unless explicitly configured  |
|                          | to be internal.                                   |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_INTERNAL = True                         |
|                          |                                                   |
|                          | See also `internal and external packages`_.       |
+--------------------------+---------------------------------------------------+
| .. _CONF_PREFIX:         |                                                   |
|                          |                                                   |
| ``PREFIX``               | Specifies the sysroot prefix value to use for the |
|                          | package. An explicitly provided prefix value will |
|                          | override the project-defined or default sysroot   |
|                          | prefix value.                                     |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_PREFIX = '/usr'                         |
|                          |                                                   |
|                          | See also |CONF_SYSROOT_PREFIX|_.                  |
+--------------------------+---------------------------------------------------+
| .. _CONF_REVISION:       |                                                   |
|                          |                                                   |
| ``REVISION``             | Specifies a revision value for a package. When a  |
|                          | package fetches content using source management   |
|                          | tools, the revision value is used to determine    |
|                          | which sources should be acquired (e.g. a tag). If |
|                          | a revision is not defined package, a package will |
|                          | use the configured |CONF_VERSION|_.               |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_REVISION = 'libfoo-v2.1'                |
|                          |                                                   |
|                          | See also |CONF_DEVMODE_REV|_ and |CONF_VERSION|_. |
+--------------------------+---------------------------------------------------+
| ``STRIP_COUNT``          | Specifies the strip count to use when attempting  |
|                          | to extract sources from an archive. By default,   |
|                          | the extraction process will strip a single        |
|                          | directory from an archive (value: 1). If a        |
|                          | package's archive has no container directory, a   |
|                          | strip count of zero can be set; likewise if an    |
|                          | archive contains multiple container directories,  |
|                          | a higher strip count can be set.                  |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_STRIP_COUNT = 1                         |
|                          |                                                   |
+--------------------------+---------------------------------------------------+
| .. _CONF_VCS_TYPE:       |                                                   |
|                          |                                                   |
| ``VCS_TYPE``             | Explicitly sets the version control system type   |
|                          | to use when acquiring sources. releng-tool        |
|                          | attempts to automatically determine the VCS type  |
|                          | of a package based off a |CONF_SITE|_ value. In   |
|                          | some scenarios, a site value may be unable to     |
|                          | specify a desired prefix/postfix. A developer can |
|                          | instead explicitly set the VCS type to be used no |
|                          | matter what the site value is configured as.      |
|                          |                                                   |
|                          | Supported types are as follows:                   |
|                          |                                                   |
|                          | - ``bzr`` (Bazaar)                                |
|                          | - ``cvs`` (CVS)                                   |
|                          | - ``git`` (Git)                                   |
|                          | - ``hg``  (Mercurial)                             |
|                          | - ``none`` (no VCS; virtual package)              |
|                          | - ``scp`` (SCP)                                   |
|                          | - ``svn`` (SVN)                                   |
|                          | - ``url`` (URL)                                   |
|                          |                                                   |
|                          | .. code-block:: python                            |
|                          |                                                   |
|                          |    LIBFOO_VCS_TYPE = 'git'                        |
|                          |                                                   |
|                          | If a project registers a custom extension which   |
|                          | provides a custom VCS type, the extension type    |
|                          | can be set in this option.                        |
|                          |                                                   |
|                          | Using a specific type will create a dependency    |
|                          | for a project that the respective host tool is    |
|                          | installed on the host system. For example, if a   |
|                          | Git VCS-type is set, the host system will need to |
|                          | have ``git`` installed on the system.             |
+--------------------------+---------------------------------------------------+

.. |CONF_DEVMODE_REV| replace:: ``DEVMODE_REVISION``
.. |CONF_EXTERNAL| replace:: ``EXTERNAL``
.. |CONF_INTERNAL| replace:: ``INTERNAL``
.. |CONF_PREFIX| replace:: ``PREFIX``
.. |CONF_REVISION| replace:: ``REVISION``
.. |CONF_VCS_TYPE| replace:: ``VCS_TYPE``

package post-processing
~~~~~~~~~~~~~~~~~~~~~~~

Every package, no matter which package |CONF_TYPE|_ is defined, can create a
post-processing script to invoke after a package has completed an installation
stage. The existence of a ``<package>-post`` inside a package directory will
trigger the post-processing stage for the package. An example post-processing
script (``libfoo-post``) can be as follows:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   print('perform post-processing work')

A post-processing script for a package is optional; thus, if a script is not
provided, no post-processing will be performed for the package.

See also `script helpers`_ for helper functions/variables available for use.

.. _site_definitions:

site definitions
~~~~~~~~~~~~~~~~

The following outlines the details for defining supported site definitions. If
attempting to use an extension-provided site type, please consult the
documentation provided by said extension.

.. note::

   All site values can be defined with a prefix value (e.g. ``git+`` for Git
   sources) or postfix value; however, this is optional if a package wishes to
   use the |CONF_VCS_TYPE|_ option.

bazaar site
^^^^^^^^^^^

To define a Bazaar_-based location, the site value must be prefixed with a
``bzr+`` value. A site can be defined as follows:

.. code-block:: python

   LIBFOO_SITE = 'bzr+ssh://example.com/project/trunk'
   # (or)
   LIBFOO_SITE = 'bzr+lp:<project>'

The value after the prefix is a path which will be provided to a ``bzr export``
call [#bzrexport]_. Content from a Bazaar repository will be fetched and
archived into a file during fetch stage. Once an cached archive is made, the
fetch stage will be skipped unless the archive is manually removed.

cvs site
^^^^^^^^

To define a CVS_-based location, the site value must be prefixed with a ``cvs+``
value. A site can be defined as follows:

.. code-block:: python

   LIBFOO_SITE = 'cvs+:pserver:anonymous@cvs.example.com:/var/lib/cvsroot mymodule'

The value after the prefix is a space-separated pair, where the first part
represents the CVSROOT [#cvsroot]_ to use and the second part specifies the CVS
module [#cvsmodule]_  to use. Content from a CVS repository will be fetched and
archived into a file during fetch stage. Once an cached archive is made, the
fetch stage will be skipped unless the archive is manually removed.

git site
^^^^^^^^

To define a Git_-based location, the site value must be prefixed with a ``git+``
value or postfixed with the ``.git`` value. A site can be defined as follows:

.. code-block:: python

   LIBFOO_SITE = 'https://example.com/libfoo.git'
   # (or)
   LIBFOO_SITE = 'git+git@example.com:base/libfoo.git'

The site value (less prefix, if used) is used as a Git remote [#gitremote]_ for
a locally managed cache source. Git sources will be cached inside the ``cache``
directory on first-run. Future runs to fetch a project's source will use the
cached Git file system. If a desired revision exists, content will be acquired
from the cache location. If a desired revision does not exist, the origin remote
will be fetched for the new revision (if it exists).

mercurial site
^^^^^^^^^^^^^^

To define a Mercurial_-based location, the site value must be prefixed with a
``hg+`` value. A site can be defined as follows:

.. code-block:: python

   LIBFOO_SITE = 'hg+https://example.com/project'

The value after the prefix is used as the ``SOURCE`` in an ``hg clone`` call
[#hgclone]_. Mercurial sources will be cached inside the ``cache`` directory on
first-run. Future runs to fetch a project's source will use the cached Mercurial
repository. If a desired revision exists, content will be acquired from the
cache location. If a desired revision does not exist, the origin remote will be
pulled for the new revision (if it exists).

scp site
^^^^^^^^

To define an SCP-based location, the site value must be prefixed with a ``scp+``
value. A site can be defined as follows:

.. code-block:: python

   LIBFOO_SITE = 'scp+TODO'

The value after the prefix is a path which will be provided to a ``scp`` call's
[#scpcommand]_ source host value. The SCP site only supports copying a file from
a remote host. The fetched file will be stored inside the ``dl`` directory. Once
fetch, the fetch stage will be skipped unless the file is manually removed.

svn site
^^^^^^^^

To define a Subversion_-based location, the site value must be prefixed with a
``svn+`` value. A site can be defined as follows:

.. code-block:: python

   LIBFOO_SITE = 'svn+https://svn.example.com/repos/libfoo/c/branches/libfoo-1.2'

The value after the prefix is a path which will be provided to a
``svn checkout`` call [#svncheckout]_. Content from a Subversion repository will
be fetched and archived into a file during fetch stage. Once an cached archive
is made, the fetch stage will be skipped unless the archive is manually removed.

url site (default)
^^^^^^^^^^^^^^^^^^

All packages that do not define a helper prefix/postfix value (as seen in other
site definitions) or do not explicitly set a |CONF_VCS_TYPE|_ value (other than
``url``), will be considered a URL site. A URL site can be defined as follows:

.. code-block:: python

   LIBFOO_SITE = 'https://example.com/my-file'

The site value provided will be directly used in a URL request. URL values
supported are defined by the Python's ``urlopen`` implementation [#urlopen]_,
which includes (but not limited to) ``http(s)://``, ``ftp://``, ``file://`` and
more.

.. _hash_files:

hash file
~~~~~~~~~

When downloading assets from a remote instance, a package's hash file can be
used to help verify the integrity of any fetched content. For example, if a
package lists a host with a ``my-archive.tgz`` to download, the fetch process
will download the archive and verify its hash to a listed entry before
continuing. If a hash does not match, the build process stops indicating an
unexpected asset was downloaded.

It is recommended that:

- Any URL-based site asset have a hash entry defined for the asset (to ensure
  the package sources are not corrupted or have been unexpectedly replaced).
- A hash entry should exist for license files (additional sanity check if a
  package's license has change).

To create a hash file for a package, add a ``<my-package>.hash`` file inside the
package's directory. The hash file should be a UTF-8 encoded file and can
contain multiple hash entries. A hash entry is a 3-tuple defining the type of
hash algorithm used, the hash value expected and the asset associated with the
hash. A tuple entry is defined on a single line with each entry separated by
whitespace characters. For example:

.. code-block:: text

   # my hashes
   sha1 f606cb022b86086407ad735bf4ec83478dc0a2c5 my-archive.tgz
   sha1 602effb4893c7504ffee8a8efcd265d86cd21609 LICENSE

Comments are permitted in the file. Lines leading with a ``#`` character or
inlined leading ``#`` character after a whitespace character will be ignored.

Officially supported hash types are FIPS-180 algorithms (``sha1``, ``sha224``,
``sha256``, ``sha384`` and ``sha512``) as well as (but not recommended) RSA'S
MD5 algorithm. Other algorithms, while unofficially supported, can be used if
provided by the system's OpenSSL library.

Multiple hash entries can be provided for the same file if desired. This is to
assist in scenarios where a checked out asset's content changes based on the
system it is checked out on. For example, a text file checked out from Git may
use Windows line-ending on Windows system, and Unix-line endings on other
systems:

.. code-block:: text

   sha1 602effb4893c7504ffee8a8efcd265d86cd21609 LICENSE
   sha1 9e79b84ef32e911f8056d80a311cf281b2121469 LICENSE

script package (default)
~~~~~~~~~~~~~~~~~~~~~~~~

A script-based package is the most basic package type available. By default,
packages are considered to be script packages unless explicitly configured to be
another package type (|CONF_TYPE|_). If a developer wishes to explicitly
configure a project as script-based, the following configuration can be used:

.. code-block:: python

   LIBFOO_TYPE = 'script'

A script package has the ability to define three Python stage scripts:

- ``<package>-configure`` - script to invoke during the configuration stage
- ``<package>-build`` - script to invoke during the build stage
- ``<package>-install`` - script to invoke during the installation stage
- ``<package>-post`` - script to invoke after the installation stage

An example build script (``libfoo-build``) can be as follows:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   releng_execute(['make'])

When a package performs a configuration, build or installation stage; the
respective script (mentioned above) will be invoked. Package scripts are
optional; thus, if a script is not provided for a stage, the stage will be
skipped.

See also `script helpers`_ for helper functions/variables available for use.

autotools package
~~~~~~~~~~~~~~~~~

An autotools package provides support for processing a `GNU Build System`_
supported module.

.. code-block:: python

   LIBFOO_TYPE = 'autotools'

When an autotools package performs a configuration stage, the package may invoke
``autoreconf`` (if configured to do so) and then invoke ``configure``. When the
build stage is reached, ``make`` will be invoked followed by ``make install``
during the installation stage.

The following configuration options are available for an autotools package:

+----------------------------+-------------------------------------------------+
| ``AUTOTOOLS_AUTORECONF``   | Specifies whether or not the package needs to   |
|                            | perform an autotools re-configuration. This is  |
|                            | to assist in the rebuilding of GNU Build System |
|                            | files which may be broken or a patch has        |
|                            | introduced new build script changes that need   |
|                            | to be applied. This field is optional. By       |
|                            | default, ``autoreconf`` is not invoked.         |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_AUTOTOOLS_AUTORECONF = True           |
+----------------------------+-------------------------------------------------+
| ``AUTOTOOLS_CONF_ENV``     | Provides a means to pass environment variables  |
|                            | into the configuration process. This option is  |
|                            | defined as a dictionary with key-value pairs    |
|                            | where the key is the environment name and the   |
|                            | value is the environment variable's value. This |
|                            | field is optional.                              |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_AUTOTOOLS_CONF_ENV = {                |
|                            |        'OPTION': 'VALUE',                       |
|                            |    }                                            |
+----------------------------+-------------------------------------------------+
| ``AUTOTOOLS_CONF_OPTS``    | Provides a means to pass command line options   |
|                            | into the configuration process. This option can |
|                            | be defined as a dictionary of string pairs or a |
|                            | list with strings -- either way defined will    |
|                            | generate argument values to include in the      |
|                            | configuration event. This field is optional.    |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_AUTOTOOLS_CONF_OPTS = {               |
|                            |        # adds "--option value" to the command   |
|                            |        '--option': 'value',                     |
|                            |    }                                            |
|                            |                                                 |
|                            |    # (or)                                       |
|                            |                                                 |
|                            |    LIBFOO_AUTOTOOLS_CONF_OPTS = [               |
|                            |        # adds "--some-option" to the command    |
|                            |        '--some-option',                         |
|                            |    ]                                            |
+----------------------------+-------------------------------------------------+
| ``AUTOTOOLS_ENV``          | Provides a means to pass environment variables  |
|                            | into the build process. This option is defined  |
|                            | as a dictionary with key-value pairs where the  |
|                            | key is the environment name and the value is    |
|                            | the environment variable's value. This field is |
|                            | optional.                                       |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_AUTOTOOLS_ENV = {                     |
|                            |        'OPTION': 'VALUE',                       |
|                            |    }                                            |
+----------------------------+-------------------------------------------------+
| ``AUTOTOOLS_INSTALL_ENV``  | Provides a means to pass environment variables  |
|                            | into the installation process. This option is   |
|                            | defined as a dictionary with key-value pairs    |
|                            | where the key is the environment name and the   |
|                            | value is the environment variable's value. This |
|                            | field is optional.                              |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_AUTOTOOLS_INSTALL_ENV = {             |
|                            |        'OPTION': 'VALUE',                       |
|                            |    }                                            |
+----------------------------+-------------------------------------------------+
| ``AUTOTOOLS_INSTALL_OPTS`` | Provides a means to pass command line options   |
|                            | into the installation process. This option can  |
|                            | be defined as a dictionary of string pairs or a |
|                            | list with strings -- either way defined will    |
|                            | generate argument values to include in the      |
|                            | installation event. This field is optional.     |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_AUTOTOOLS_INSTALL_OPTS = {            |
|                            |        # adds "--option value" to the command   |
|                            |        '--option': 'value',                     |
|                            |    }                                            |
|                            |                                                 |
|                            |    # (or)                                       |
|                            |                                                 |
|                            |    LIBFOO_AUTOTOOLS_INSTALL_OPTS = [            |
|                            |        # adds "--some-option" to the command    |
|                            |        '--some-option',                         |
|                            |    ]                                            |
+----------------------------+-------------------------------------------------+
| ``AUTOTOOLS_OPTS``         | Provides a means to pass command line options   |
|                            | into the build process. This option can         |
|                            | be defined as a dictionary of string pairs or a |
|                            | list with strings -- either way defined will    |
|                            | generate argument values to include in the      |
|                            | build event. This field is optional.            |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_AUTOTOOLS_OPTS = {                    |
|                            |        # adds "--option value" to the command   |
|                            |        '--option': 'value',                     |
|                            |    }                                            |
|                            |                                                 |
|                            |    # (or)                                       |
|                            |                                                 |
|                            |    LIBFOO_AUTOTOOLS_OPTS = [                    |
|                            |        # adds "--some-option" to the command    |
|                            |        '--some-option',                         |
|                            |    ]                                            |
+----------------------------+-------------------------------------------------+

cmake package
~~~~~~~~~~~~~

A CMake package provides support for processing a `CMake`_ supported module.

During the configuration stage of a CMake package, ``cmake`` will be invoked to
generate build files for the module. For the build stage, ``cmake --build`` will
be invoked to generated build files. Similar approach for the installation stage
where the build option is invoked again but with the ``install`` target invoked:
``cmake --build --target install``. Each stage can be configured to manipulate
environment variables and options used by the CMake executable.

The default configuration built for projects is ``RelWithDebInfo``. A developer
can override this option by explicitly adjusting the configuration option
``--config`` to, for example, ``Debug``:

.. code-block:: python

   LIBFOO_CMAKE_OPTS = {
      '--config': 'Debug',
   }

   LIBFOO_CMAKE_INSTALL_OPTS = {
      '--config': 'Debug',
   }

The following configuration options are available for a CMake package:

+----------------------------+-------------------------------------------------+
| ``CMAKE_CONF_DEFS``        | Provides a means to pass definitions into the   |
|                            | configuration process. This option can is       |
|                            | defined as a dictionary of string pairs. This   |
|                            | field is optional.                              |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_CMAKE_CONF_DEFS = {                   |
|                            |        'CMAKE_BUILD_TYPE': 'RelWithDebInfo',    |
|                            |    }                                            |
+----------------------------+-------------------------------------------------+
| ``CMAKE_CONF_ENV``         | Provides a means to pass environment variables  |
|                            | into the configuration process. This option is  |
|                            | defined as a dictionary with key-value pairs    |
|                            | where the key is the environment name and the   |
|                            | value is the environment variable's value. This |
|                            | field is optional.                              |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_CMAKE_CONF_ENV = {                    |
|                            |        'OPTION': 'VALUE',                       |
|                            |    }                                            |
+----------------------------+-------------------------------------------------+
| ``CMAKE_CONF_OPTS``        | Provides a means to pass command line options   |
|                            | into the configuration process. This option can |
|                            | be defined as a dictionary of string pairs or a |
|                            | list with strings -- either way defined will    |
|                            | generate argument values to include in the      |
|                            | configuration event. This field is optional.    |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_CMAKE_CONF_OPTS = {                   |
|                            |        # adds "--option value" to the command   |
|                            |        '--option': 'value',                     |
|                            |    }                                            |
|                            |                                                 |
|                            |    # (or)                                       |
|                            |                                                 |
|                            |    LIBFOO_CMAKE_CONF_OPTS = [                   |
|                            |        # adds "--some-option" to the command    |
|                            |        '--some-option',                         |
|                            |    ]                                            |
+----------------------------+-------------------------------------------------+
| ``CMAKE_ENV``              | Provides a means to pass environment variables  |
|                            | into the build process. This option is defined  |
|                            | as a dictionary with key-value pairs where the  |
|                            | key is the environment name and the value is    |
|                            | the environment variable's value. This field is |
|                            | optional.                                       |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_CMAKE_ENV = {                         |
|                            |        'OPTION': 'VALUE',                       |
|                            |    }                                            |
+----------------------------+-------------------------------------------------+
| ``CMAKE_INSTALL_ENV``      | Provides a means to pass environment variables  |
|                            | into the installation process. This option is   |
|                            | defined as a dictionary with key-value pairs    |
|                            | where the key is the environment name and the   |
|                            | value is the environment variable's value. This |
|                            | field is optional.                              |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_CMAKE_INSTALL_ENV = {                 |
|                            |        'OPTION': 'VALUE',                       |
|                            |    }                                            |
+----------------------------+-------------------------------------------------+
| ``CMAKE_INSTALL_OPTS``     | Provides a means to pass command line options   |
|                            | into the installation process. This option can  |
|                            | be defined as a dictionary of string pairs or a |
|                            | list with strings -- either way defined will    |
|                            | generate argument values to include in the      |
|                            | installation event. This field is optional.     |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_CMAKE_INSTALL_OPTS = {                |
|                            |        # adds "--option value" to the command   |
|                            |        '--option': 'value',                     |
|                            |    }                                            |
|                            |                                                 |
|                            |    # (or)                                       |
|                            |                                                 |
|                            |    LIBFOO_CMAKE_INSTALL_OPTS = [                |
|                            |        # adds "--some-option" to the command    |
|                            |        '--some-option',                         |
|                            |    ]                                            |
+----------------------------+-------------------------------------------------+
| ``CMAKE_OPTS``             | Provides a means to pass command line options   |
|                            | into the build process. This option can         |
|                            | be defined as a dictionary of string pairs or a |
|                            | list with strings -- either way defined will    |
|                            | generate argument values to include in the      |
|                            | build event. This field is optional.            |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_CMAKE_OPTS = {                        |
|                            |        # adds "--option value" to the command   |
|                            |        '--option': 'value',                     |
|                            |    }                                            |
|                            |                                                 |
|                            |    # (or)                                       |
|                            |                                                 |
|                            |    LIBFOO_CMAKE_OPTS = [                        |
|                            |        # adds "--some-option" to the command    |
|                            |        '--some-option',                         |
|                            |    ]                                            |
+----------------------------+-------------------------------------------------+

python package
~~~~~~~~~~~~~~

A Python package provides support for processing a `Python`_ supported module.

Only the build and installation phases are used when processing the sources for
a Python package (i.e. no configuration stage is invoked). The build phase will
invoke ``setup.py build`` while the installation stage will invoke
``setup.py install``. When a Python package is process, it will use the system's
default Python interpreter. A developer can override what Python interpreter to
use by configuring the ``PYTHON_INTERPRETER`` option in a package:

.. code-block:: python

   LIBFOO_PYTHON_INTERPRETER = '/opt/my-custom-python-build/python'

The following configuration options are available for a Python package:


+----------------------------+-------------------------------------------------+
| ``PYTHON_ENV``             | Provides a means to pass environment variables  |
|                            | into the build process. This option is defined  |
|                            | as a dictionary with key-value pairs where the  |
|                            | key is the environment name and the value is    |
|                            | the environment variable's value. This field is |
|                            | optional.                                       |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_PYTHON_ENV = {                        |
|                            |        'OPTION': 'VALUE',                       |
|                            |    }                                            |
+----------------------------+-------------------------------------------------+
| ``PYTHON_INSTALL_ENV``     | Provides a means to pass environment variables  |
|                            | into the installation process. This option is   |
|                            | defined as a dictionary with key-value pairs    |
|                            | where the key is the environment name and the   |
|                            | value is the environment variable's value. This |
|                            | field is optional.                              |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_PYTHON_INSTALL_ENV = {                |
|                            |        'OPTION': 'VALUE',                       |
|                            |    }                                            |
+----------------------------+-------------------------------------------------+
| ``PYTHON_INSTALL_OPTS``    | Provides a means to pass command line options   |
|                            | into the installation process. This option can  |
|                            | be defined as a dictionary of string pairs or a |
|                            | list with strings -- either way defined will    |
|                            | generate argument values to include in the      |
|                            | installation event. This field is optional.     |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_PYTHON_INSTALL_OPTS = {               |
|                            |        # adds "--option value" to the command   |
|                            |        '--option': 'value',                     |
|                            |    }                                            |
|                            |                                                 |
|                            |    # (or)                                       |
|                            |                                                 |
|                            |    LIBFOO_PYTHON_INSTALL_OPTS = [               |
|                            |        # adds "--some-option" to the command    |
|                            |        '--some-option',                         |
|                            |    ]                                            |
+----------------------------+-------------------------------------------------+
| ``PYTHON_INTERPRETER``     | Defines an specific Python interpreter when     |
|                            | processing the build and installation stages    |
|                            | for a package. If not specified, the system's   |
|                            | Python interpreter will be used. This field is  |
|                            | optional.                                       |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_PYTHON_INTERPRETER = '<path>'         |
+----------------------------+-------------------------------------------------+
| ``PYTHON_OPTS``            | Provides a means to pass command line options   |
|                            | into the build process. This option can         |
|                            | be defined as a dictionary of string pairs or a |
|                            | list with strings -- either way defined will    |
|                            | generate argument values to include in the      |
|                            | build event. This field is optional.            |
|                            |                                                 |
|                            | .. code-block:: python                          |
|                            |                                                 |
|                            |    LIBFOO_PYTHON_OPTS = {                       |
|                            |        # adds "--option value" to the command   |
|                            |        '--option': 'value',                     |
|                            |    }                                            |
|                            |                                                 |
|                            |    # (or)                                       |
|                            |                                                 |
|                            |    LIBFOO_PYTHON_OPTS = [                       |
|                            |        # adds "--some-option" to the command    |
|                            |        '--some-option',                         |
|                            |    ]                                            |
+----------------------------+-------------------------------------------------+

other
-----

post-processing
~~~~~~~~~~~~~~~

.. warning::

   A post-processing script (if used) will be invoked each time ``releng-tool``
   reaches the final stage of a build.

After each package has been processed, a project has the ability to perform
post-processing. Post-processing allows a developer to cleanup the target
directory, build an archive/package from generated results and more. If a
project contains a ``post.py`` inside the root directory, the post-processing
script will be invoked in the final stage of a build.

A developer may start out with the following post-processing script
``<root>/post.py``:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   print('post processing...')

The above script will output the newly inserted print message at the end of a
build process:

.. code-block:: shell

   $ releng-tool
   ...
   generating license information...
   post processing...
   (success) completed (0:01:30)

A developer can take advantage of `environment variables`_ and
`script helpers`_ for additional support.

It is important to note that a post-processing script will be invoked each time
a ``releng-tool`` invoke reaches the final stage of a build. A developer should
attempt to implement the post-processing script in a way that it can be invoked
multiple times. For example, if a developer decides to move a file out of the
target directory into an interim directory when building an archive, it is most
likely that a subsequent request to build may fail since the file can no longer
be found inside the target directory.

.. _license_information:

licenses
~~~~~~~~

A releng-tool project can defined multiple packages, each with the possibility
of having multiple licenses associated with them. Each project may vary: some
may have only proprietary sources and may not care about tracking this
information; some may only use open source software and require to populate
license information for a final package; or a mix.

When license information is populated for a project, each project's license
information (|CONF_LICENSE_FILES|_) is will be populated into a single license
document. If a developer defines the |CONF_LICENSE_HEADER|_ configuration,
the generated document will be prefixed with the header content. For example,
``releng.py`` can be configured to prepare a license header from a local file
``assets/license-header.tpl``:

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   import os

   ... (other configuration options)

   root_dir = os.path.dirname(os.path.realpath(__file__))
   license_header_file = os.path.join(root_dir, 'assets', 'license-header.tpl')

   with open(license_header_file) as f:
       license_header = ''.join(f.readlines())

A side note is that licenses for a project are generated before the
`post-processing`_ phase; hence, generated license document(s) may be included
when attempting to generated final archives/packages.

patching
~~~~~~~~

.. note::

   Patches are ignored when in :ref:`development mode` for packages with a
   development version revision or when in :ref:`local-sources mode` for
   internal packages.

The patching stage for a package provides the ability for a developer to apply
one or more patches to extracted sources. A project may define an external
package which fetches an archive that is not maintained by the project owners.
The fetched source may not be able to build in a developer's releng-tool project
due to limitations of the implementation or build scripts provided by the
package. A developer can prepare a series of patches to apply to a package and
submit changes upstream to correct the issue; however, the developer is then
left to either wait for the changes to be merged in or needs to make a custom
archive with the appropriate modifications already applied. To avoid this, a
developer can include patches directly in the package folder to be automatically
applied during patching stage.

When a package's patch stage is reached, releng-tool will look for patches found
inside the package folder with the extension ``.patch``. Patches found inside a
package folder are applied in ascending order. It is recommended to prefix
patch filenames with a numerical value for clarity. For example, the following
package patches:

.. code-block:: shell

   $ cd package/liba
   $ ls *.patch
   0001-accept-linker-flags.patch
   0002-correct-output-path.patch
   0003-support-disabling-test-build.patch
   liba
   lib.hash

With be applied in the following order:

1. ``0001-accept-linker-flags.patch``
2. ``0002-correct-output-path.patch``
3. ``0003-support-disabling-test-build.patch``

If a user configures their build environment in :ref:`development mode`, patches
will not be applied if a package defines a development revisions. The idea is
that a development revision is most likely the bleeding edge source of a
package and does not need any patches. If a user configures their build
environment in :ref:`local-sources mode` and a package is defined as internal,
patches will not be applied to the sources. This is to prevent the patching
system from making unexpected modifications to a developer's local source
variants.

internal and external packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Packages are either internal packages or external packages. All packages are
considered external packages by default unless explicitly configured as internal
through either the package option |CONF_INTERNAL|_ or using the project
configuration |CONF_DEFAULT_INTERN|_ (see also |CONF_EXTERNAL|_). Both package
types are almost treated the same except for the following:

- An internal package will not generate output warnings if the package is
  missing :ref:`hash information <hash_files>`.
- An internal package will not generate output warnings if the package is
  missing :ref:`license information <license_information>`.
- When configured for :ref:`development mode`; the patch stage will not be
  performed if the package specifies a development revision
  (|CONF_DEVMODE_REV|_).
- When configured for :ref:`local-sources mode`; the fetch, extract and patch
  stages will not be performed.

script helpers
~~~~~~~~~~~~~~

releng-tool provides a series of helper functions which can be used in
script-based packages, post-processing and more. Helper functions provided are
listed below:

+--------------------------+---------------------------------------------------+
| method                   | documentation                                     |
+==========================+===================================================+
| ``debug``                | .. automodule:: releng                            |
|                          |     :members: debug                               |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``err``                  | .. automodule:: releng                            |
|                          |     :members: err                                 |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``log``                  | .. automodule:: releng                            |
|                          |     :members: log                                 |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``note``                 | .. automodule:: releng                            |
|                          |     :members: note                                |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``releng_copy``          | .. automodule:: releng                            |
|                          |     :members: releng_copy                         |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``releng_execute``       | .. automodule:: releng                            |
|                          |     :members: releng_execute                      |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``releng_exists``        | .. automodule:: releng                            |
|                          |     :members: releng_exists                       |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``releng_exit``          | .. automodule:: releng                            |
|                          |     :members: releng_exit                         |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``releng_expand``        | .. automodule:: releng                            |
|                          |     :members: releng_expand                       |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``releng_join``          | .. automodule:: releng                            |
|                          |     :noindex:                                     |
|                          |                                                   |
|                          |     .. method:: releng_join(path, *paths)         |
|                          |                                                   |
|                          |        An alias for |os.path.join|_.              |
+--------------------------+---------------------------------------------------+
| ``releng_move``          | .. automodule:: releng                            |
|                          |     :members: releng_move                         |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``releng_remove``        | .. automodule:: releng                            |
|                          |     :members: releng_remove                       |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``releng_tmpdir``        | .. automodule:: releng                            |
|                          |     :members: releng_tmpdir                       |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``releng_touch``         | .. automodule:: releng                            |
|                          |     :members: releng_touch                        |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``releng_wd``            | .. automodule:: releng                            |
|                          |     :members: releng_wd                           |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``success``              | .. automodule:: releng                            |
|                          |     :members: success                             |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``verbose``              | .. automodule:: releng                            |
|                          |     :members: verbose                             |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+
| ``warn``                 | .. automodule:: releng                            |
|                          |     :members: warn                                |
|                          |     :noindex:                                     |
+--------------------------+---------------------------------------------------+

.. |os.path.join| replace:: ``os.path.join``
.. _os.path.join: https://docs.python.org/library/os.path.html#os.path.join

Scripts directly invoked by releng-tool will automatically have these helpers
registered in the script's globals module (i.e. no import is necessary). If a
project defines custom Python modules in their project and wishes to take
advantage of these helper functions, the following import can be used to, for
example, import a specific function:

.. code-block:: python

    from releng import releng_execute

Or, if desired, all helper methods can be imported at once:

.. code-block:: python

    from releng import *

vcs ignore
~~~~~~~~~~

When invoking releng-tool on a project, the project's root directory will be
populated with cached assets and other output files. A series of standard ignore
patterns can be applied to a repository to prevent observing these generated
files using VCS tools. The following is an example ignore configuration which
can be applied for Git-based repositories (via ``.gitignore``):

.. code-block:: text

   # releng-tool
   /cache/
   /dl/
   /output/
   .releng-flag-*

loading extensions
~~~~~~~~~~~~~~~~~~

.. note::

   If looking for information on developing extensions for releng-tool, consult
   the :ref:`contributor's guide -- extensions <contributor_guide_ext>`.

A releng-tool project can define one or more extensions to load for externally
implemented capabilities. For example, a project can load extensions
``ext-a`` and ``ext-b`` with the following defined in their project's
configuration:

.. code-block:: python

   extensions = [
       'ext-a',
       'ext-b',
   ]

During the initial stages of a release engineering process, releng-tool will
check and load any configured extension. In the event that an extension is
missing, is unsupported for the running releng-tool version or fails to load, a
detailed error message will be presented to the user.

While the ability to load extensions is supported, capabilities provided by
extensions are not officially supported by releng-tool. For issues related to
specific extension use, it is recommended to consult the documentation provided
by the providers of said extensions.

.. footnotes

.. [#bzrexport] http://doc.bazaar.canonical.com/bzr.2.7/en/user-reference/export-help.html
.. [#cvsmodule] https://www.gnu.org/software/trans-coord/manual/cvs/html_node/checkout.html#checkout
.. [#cvsroot] https://www.gnu.org/software/trans-coord/manual/cvs/html_node/Specifying-a-repository.html
.. [#gitremote] https://git-scm.com/docs/git-remote
.. [#hgclone] https://www.selenic.com/mercurial/hg.1.html#clone
.. [#scpcommand] https://linux.die.net/man/1/scp
.. [#svncheckout] http://svnbook.red-bean.com/en/1.7/svn.ref.svn.c.checkout.html
.. [#urlopen] https://docs.python.org/3.7/library/urllib.request.html#urllib.request.urlopen

.. references

.. _Bazaar: https://bazaar.canonical.com
.. _CMake: https://cmake.org/
.. _CVS: http://cvs.nongnu.org/
.. _GNU Build System: https://www.gnu.org/software/automake/manual/html_node/index.html
.. _Git: https://git-scm.com/
.. _Mercurial: https://www.mercurial-scm.org/
.. _Python: https://www.python.org/
.. _Subversion: https://subversion.apache.org/
