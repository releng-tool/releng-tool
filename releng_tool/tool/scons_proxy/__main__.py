# -*- coding: utf-8 -*-
# Copyright 2022 releng-tool
#
# This is a utility module to help load a legacy version of SCons. typically
# found in older Python interpreters (i.e. Python 2.7 and Python 3.4). For
# older installs, the SCons module is found inside a `scons` directory. This
# helper module will append this folder into the system path, import it and
# invoke the module's mainline script.

from importlib import import_module
import os
import site
import sys


# inject the scons container folder in the site path
for site_base in site.getsitepackages():
    scons_container = os.path.join(site_base, 'scons')
    if os.path.exists(scons_container):
        sys.path.append(scons_container)

if sys.version_info < (3, 5):
    # Scons' `_load_dotted_module_py2` implementation used in Python 3.4 does
    # not function as expected (where tools may fail to load). To help deal
    # with this, we will override the load operation in attempt to perform
    # a simple `import_module` call (which should handle the case for
    # Python 3.4). Any failed attempt to load the module will fallback on
    # the original implementation.
    import SCons.Tool  # pylint: disable=E0401
    orig_load = SCons.Tool.Tool._load_dotted_module_py2

    try:
        RelengModuleNotFoundError = ModuleNotFoundError
    except NameError:
        RelengModuleNotFoundError = ImportError

    def load_override(self, short_name, full_name, searchpaths=None):
        try:
            # Some SCons versions may not have the "full name" properly set;
            # if the full name prefix is not set, add it before attempting
            # to load the module.
            prefix = 'SCons.Tool.'
            target_full_name = full_name
            if not full_name.startswith(prefix):
                target_full_name = prefix + full_name

            plugin = import_module(target_full_name)
            return plugin, None
        except RelengModuleNotFoundError:
            pass

        return orig_load(self, short_name, full_name, searchpaths=searchpaths)

    SCons.Tool.Tool._load_dotted_module_py2 = load_override

# invoke the mainline script
if __name__ == '__main__':
    import SCons.Script  # pylint: disable=E0401
    SCons.Script.main()
