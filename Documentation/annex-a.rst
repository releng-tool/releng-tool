annex a - quick reference
=========================

A quick reference document listing available options to developers building a
releng-tool project. Consult the :doc:`developer's guide <developer-guide>` for
more detailed information.

configuration options
---------------------

Options which are read by releng-tool from a project's configuration script:

.. code-block:: python

   cache_ext = <function>
   default_internal = bool
   extensions = ['<extension>', '<extension>']
   external_packages = ['<path>', '<path>']
   license_header = '<data>'
   override_extract_tools = {'<extension>': '<tool-path>'}
   override_revisions = {'<pkg>': '<revision>'}
   override_sites = {'<pkg>': '<site>'}
   packages = ['<pkg>', '<pkg>', '<pkg>']
   quirks = ['<quirk-id>']
   sysroot_prefix = '<path>' # '/usr'
   url_mirror = '<mirror-url>'

environment variables
---------------------

Environment (and script) variables available to context's invoked by
releng-tool (may vary per context):

.. code-block:: python

   BUILD_DIR
   CACHE_DIR
   DL_DIR
   HOST_DIR
   IMAGES_DIR
   LICENSE_DIR
   NJOBS
   NJOBSCONF
   OUTPUT_DIR
   PKG_BUILD_DIR
   PKG_BUILD_OUTPUT_DIR
   PKG_CACHE_DIR
   PKG_CACHE_FILE
   PKG_DEFDIR
   PKG_INTERNAL
   PKG_NAME
   PKG_REVISION
   PKG_SITE
   PKG_VERSION
   PREFIX
   RELENG_REBUILD
   RELENG_RECONFIGURE
   RELENG_REINSTALL
   ROOT_DIR
   STAGING_DIR
   SYMBOLS_DIR
   TARGET_DIR
   <PKG_NAME>_BUILD_DIR
   <PKG_NAME>_BUILD_OUTPUT_DIR
   <PKG_NAME>_NAME
   <PKG_NAME>_REVISION
   <PKG_NAME>_VERSION

package options
---------------

Configuration options parsed by releng-tool for a package definition:

.. code-block:: python

   LIBFOO_AUTOTOOLS_AUTORECONF = bool
   LIBFOO_BUILD_DEFS = {'FOO': 'BAR'}
   LIBFOO_BUILD_ENV = {'FOO': 'BAR'}
   LIBFOO_BUILD_OPTS = {'--option': 'value'} or ['--option', 'value']
   LIBFOO_BUILD_SUBDIR = '<subdir>'
   LIBFOO_CONF_DEFS = {'FOO': 'BAR'}
   LIBFOO_CONF_ENV = {'FOO': 'BAR'}
   LIBFOO_CONF_OPTS = {'--option': 'value'} or ['--option', 'value']
   LIBFOO_DEPENDENCIES = ['<pkg>', '<pkg>']
   LIBFOO_DEVMODE_IGNORE_CACHE = bool
   LIBFOO_DEVMODE_REVISION = '<revision>'
   LIBFOO_EXTENSION = '<extension>'
   LIBFOO_EXTERNAL = bool
   LIBFOO_EXTOPT = {'FOO': 'BAR'}
   LIBFOO_EXTRACT_TYPE = 'ext-<extraction-extension>'
   LIBFOO_FIXED_JOBS = int # >= 1
   LIBFOO_INSTALL_DEFS = {'FOO': 'BAR'}
   LIBFOO_INSTALL_ENV = {'FOO': 'BAR'}
   LIBFOO_INSTALL_OPTS = {'--option': 'value'} or ['--option', 'value']
   LIBFOO_INSTALL_TYPE = '<install-type>' # host, images, staging, staging_and_target, target
   LIBFOO_INTERNAL = bool
   LIBFOO_NO_EXTRACTION = bool
   LIBFOO_LICENSE = '<license>'  or ['<license>', '<license>']
   LIBFOO_LICENSE_FILES = '<file>' or ['<file>', '<file>']
   LIBFOO_PREFIX = '<path>' # '/usr'
   LIBFOO_PYTHON_INTERPRETER = '<path>'
   LIBFOO_REVISION = '<revision>'
   LIBFOO_SITE = '<site>'
   LIBFOO_STRIP_COUNT = int # >= 0
   LIBFOO_TYPE = '<type>' # autotools, cmake, python, script, ext-<extension>
   LIBFOO_VCS_TYPE = '<vcs-type>' # bzr, cvs, git, hg, none, scp, svn, url
   LIBFOO_VERSION = '<version>'

script helpers
--------------

Functions available to scripts invoked by releng-tool or importable via
``from releng import *``:

.. code-block:: python

   debug(msg, *args)
   err(msg, *args)
   log(msg, *args)
   note(msg, *args)
   releng_copy(src, dst, quiet=False, critical=True)
   releng_env(key, value)
   releng_execute(args, cwd=None, env=None, env_update=None, quiet=False, critical=True, poll=False, capture=None)
   releng_exists(path, *args)
   releng_exit(msg=None, code=None)
   releng_expand(obj, kv=None)
   releng_join(path, *args)
   releng_mkdir(dir, quiet=False)
   releng_move(src, dst, quiet=False, critical=True)
   releng_remove(path, quiet=False)
   releng_tmpdir(dir=None)
   releng_touch(file)
   releng_wd(dir)
   success(msg, *args)
   verbose(msg, *args)
   warn(msg, *args)
