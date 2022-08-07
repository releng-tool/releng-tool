# -*- coding: utf-8 -*-
# Copyright 2022 releng-tool
#
# This is a utility module to help load SCons via a Python interpreter
# in a Python 2.7 environment. On python 2.7, the SCons module is found
# inside a `scons` directory. This helper module will append this folder
# into the system path, import it and invoke the module's mainline
# script.

import os
import site
import sys


sys.path.append(os.path.join(site.getsitepackages()[-1], 'scons'))


if __name__ == '__main__':
    import SCons.Script  # pylint: disable=E0401
    SCons.Script.main()
