ANNEX A - Quick reference
=========================

A quick reference document listing available options to developers building a
releng-tool project. Consult the :doc:`developer's guide <developer-guide>` for
more detailed information.

Configuration options
---------------------

Options which are read by releng-tool from a project's configuration script:

.. code-block:: python

   cache_ext = <callable>
   default_internal = bool
   extensions = ['<extension>', '<extension>']
   external_packages = ['<path>', '<path>']
   license_header = '<data>'
   override_extract_tools = {'<tool>': '<tool-path>'}
   override_revisions = {'<pkg>': '<revision>'}
   override_sites = {'<pkg>': '<site>'}
   packages = ['<pkg>', '<pkg>', '<pkg>']
   prerequisites = ['<tool>', '<tool>', '<tool>']
   quirks = ['<quirk-id>']
   sysroot_prefix = '<path>' # '/usr'
   url_mirror = '<mirror-url>'
   urlopen_context = <ssl.SSLContext>

Environment variables
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
   RELENG_CLEAN
   RELENG_DEBUG
   RELENG_DEVMODE
   RELENG_DISTCLEAN
   RELENG_FORCE
   RELENG_LOCALSRCS
   RELENG_MRPROPER
   RELENG_REBUILD
   RELENG_RECONFIGURE
   RELENG_REINSTALL
   RELENG_VERBOSE
   RELENG_VERSION
   ROOT_DIR
   STAGING_DIR
   SYMBOLS_DIR
   TARGET_DIR
   <PKG_NAME>_BUILD_DIR
   <PKG_NAME>_BUILD_OUTPUT_DIR
   <PKG_NAME>_DEFDIR
   <PKG_NAME>_NAME
   <PKG_NAME>_REVISION
   <PKG_NAME>_VERSION

Package options
---------------

Configuration options parsed by releng-tool for a package definition:

.. code-block:: python

   LIBFOO_AUTOTOOLS_AUTORECONF = bool
   LIBFOO_BUILD_DEFS = {'FOO': 'BAR'}
   LIBFOO_BUILD_ENV = {'FOO': 'BAR'}
   LIBFOO_BUILD_OPTS = {'--option': 'value'} or ['--option', 'value']
   LIBFOO_BUILD_SUBDIR = '<subdir>'
   LIBFOO_CMAKE_NOINSTALL = bool
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
   LIBFOO_GIT_CONFIG = {'FOO': 'BAR'}
   LIBFOO_GIT_DEPTH = int # >= 0
   LIBFOO_GIT_REFSPECS = ['<refspec>'] # e.g. pull
   LIBFOO_GIT_SUBMODULES = bool
   LIBFOO_GIT_VERIFY_REVISION = bool
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
   LIBFOO_SKIP_REMOTE_CONFIG = bool
   LIBFOO_SKIP_REMOTE_SCRIPTS = bool
   LIBFOO_SITE = '<site>'
   LIBFOO_STRIP_COUNT = int # >= 0
   LIBFOO_TYPE = '<type>' # autotools, cmake, python, script, ext-<extension>
   LIBFOO_VCS_TYPE = '<vcs-type>' # bzr, cvs, git, hg, local, none, rsync, scp, svn, url
   LIBFOO_VERSION = '<version>'

Script helpers
--------------

Functions available to scripts invoked by releng-tool or importable via
``from releng_tool import *``:

.. code-block:: python

   debug(msg, *args)
   err(msg, *args)
   log(msg, *args)
   note(msg, *args)
   releng_cat(file, *args)
   releng_copy(src, dst, quiet=False, critical=True)
   releng_env(key, value=None)
   releng_execute(args, cwd=None, env=None, env_update=None, quiet=False, critical=True, poll=False, capture=None)
   releng_execute_rv(command, args, cwd=None, env=None, env_update=None)
   releng_exists(path, *args)
   releng_exit(msg=None, code=None)
   releng_expand(obj, kv=None)
   releng_include(file_path)
   releng_join(path, *args)
   releng_ls(dir_)
   releng_mkdir(dir_, quiet=False)
   releng_move(src, dst, quiet=False, critical=True)
   releng_remove(path, quiet=False)
   releng_require_version(version)
   releng_tmpdir(dir_=None)
   releng_touch(file)
   releng_wd(dir_)
   success(msg, *args)
   verbose(msg, *args)
   warn(msg, *args)

Quirks
------

Quirk options used by releng-tool:

.. code-block:: none

   releng.cmake.disable_parallel_option
   releng.disable_prerequisites_check
   releng.disable_remote_configs
   releng.disable_remote_scripts
   releng.git.no_depth
   releng.git.no_quick_fetch
