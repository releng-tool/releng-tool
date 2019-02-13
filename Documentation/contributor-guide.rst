contributor guide
=================

The following outlines common directory locations:

- ``Documentation`` - project documentation
- ``releng/api/`` - api implementation for supporting releng-tool extensions
- ``releng/engine/`` - core implementation
- ``releng/ext/`` - extensions that are maintained in the official tree
- ``releng/extract/`` - translating fetched content to a build's working area
- ``releng/fetch/`` - support for fetching content from package sites
- ``releng/tool/`` - definitions for host tools used by tool features
- ``test/`` - testing-related content for this project's implementation

releng-tool is built on the Python language and aims to be the minimum
dependency for users of the tool. Specific features enabled by a developer's
project may require additional tools (e.g. using Git_ to fetch sources requires
``git`` to be installed); however, a user should not be required to install
tools for features that are not being used.

contributing
------------

Developers are free to submit contributions for this project. Developers wishing
to contribute should consult this project's `CONTRIBUTING`_ document. A reminder
that any contributions must be signed off with the
`Developer Certificate of Origin`_.

root directory
--------------

A user invoking releng-tool will attempt to operate in a project root directory.
Any content managed by this tool (e.g. creating directories, downloading
sources, etc.) should all be performed inside the root directory. Some
exceptions exist where a user requests to adjust the download directory (i.e.
providing the ``--dl-dir`` argument).

fetching design
---------------

Packages can describe where external content should be fetched from. The most
common fetching method is a simple URI-style fetch such as downloading an
archive from an HTTP/FTP location. Assets acquired in this manner are downloaded
into the root directory's download folder (e.g. ``<ROOT>/dl``). The extraction
phase will later use this folder to find package content to prepare against.

releng-tool also supports the fetching of content from version control systems.
Sources can either be fetched and placed into an archive, in a similar fashion
as fetching an archive from HTTP/FTP locations, or sources can be fetched into a
"cache directory" if supported (typically distributed version controlled
sources). For example, Git_ repositories (see also Git's |--git-dir|_) will be
stored in the root directory's cache folder (e.g. ``<ROOT>/cache``). During the
extraction stage, target revisions will be pulled from the cache location using
the ``git`` client.

Not all packages will fetch content (i.e. placeholder packages).

.. |--git-dir| replace:: ``--git-dir``

extraction design
-----------------

In most cases, the extraction phase will process archives (e.g. ``.tar.gz``,
``.zip``, etc.) and place their content into a package's build working
directory. Implementation will vary for fetching implementation which stores
content into a cache directory. For example, Git_ and Mercurial_ sources have
their own extraction implementations to pull content from their respective
distributed file systems into a package's build working directory.

host and build environment
--------------------------

releng-tool attempts to minimize the impact of a host system's environment on a
project's build. For example, the build phase of a package should not be pulling
compiler flags provided from the host system's environment. These flags should
be provided from the package definition. Tools invoked by releng-tool will
attempt to be invoked to ignore these external environment variables. Some
exceptions apply such as environment variables dealing with authorization
tokens.

.. _contributor_guide_ext:

extensions
----------

Developers wishing to provide extensions to releng-tool should consult the API
implementation found in this tool's repository (|releng/api/__init__.py|_).
Implementation in the API folder aims to be "API safe" -- there is a strong
attempt to prevent the changing of classes, methods, etc. to prevent
compatibility issues as both releng-tool and extensions (if any) evolve. A
developer for a releng-tool project would register an extension to load using
the ``extensions`` configuration option inside the project configuration
(``releng.py``):

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   ...

   extensions = [
       'ext-custom',
   ]

On start, releng-tool will use this extension configuration to find and invoke
the setup stage for each available extension.

An extension will define ``releng_setup`` to be registered into releng-tool. The
call will provide an instance to the releng-tool application which allows an
extension to register custom fetching, extraction and package implementations.

.. code-block:: python

   #!/usr/bin/env python
   # -*- coding: utf-8 -*-

   import releng.api

   def releng_setup(app):
       # explicit version check for releng-tool version (if needed)
       app.require_version('<version>')

       # fetch support (for custom fetch implementation)
       app.add_fetch_type('ext-myextension', <impl>)

       # extraction support (for custom extraction implementation)
       app.add_extract_type('ext-myextension', <impl>)

       # package support (configure, build, installation modifications)
       app.add_package_type('ext-myextension', <impl>)

For more details for API details, consult the documentation found inside the
`API implementation`_.

.. |releng/api/__init__.py| replace:: ``releng/api/__init__.py``

.. _--git-dir: https://git-scm.com/docs/git#git---git-dirltpathgt
.. _API implementation: https://github.com/releng-tool/releng-tool/blob/master/releng/api/__init__.py
.. _CONTRIBUTING: https://github.com/releng-tool/releng-tool/blob/master/CONTRIBUTING.rst
.. _Developer Certificate of Origin: https://developercertificate.org/
.. _Git: https://git-scm.com/
.. _Mercurial: https://www.mercurial-scm.org/
.. _releng/api/__init__.py: https://github.com/releng-tool/releng-tool/blob/master/releng/api/__init__.py
