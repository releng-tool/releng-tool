# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

# This is a utility module to help load a legacy version of SCons. Typically
# found in older Python interpreters (i.e. Python 2.7 and Python 3.4). For
# older installs, the SCons module is found inside a `scons` directory. This
# helper module will append this folder into the system path, import it and
# invoke the module's mainline script.

import os
import site
import sys


# inject the scons container folder in the site path
for site_base in site.getsitepackages():
    scons_container = os.path.join(site_base, 'scons')
    if os.path.exists(scons_container):
        sys.path.append(str(scons_container))

# invoke the mainline script
if __name__ == '__main__':
    import SCons.Script  # pylint: disable=E0401
    SCons.Script.main()
