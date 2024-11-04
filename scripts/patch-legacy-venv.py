#!/usr/bin/env python
# Copyright releng-tool
# Copyright Python Software Foundation
# SPDX-License-Identifier: BSD-2-Clause AND PSF-2.0
#
# The following script will patch a venv's site module to include the
# `getsitepackages` function. The function is needed for some tool-related
# actions and older versions of venv did not provide support for the call.

import os
import site


def main():
    if not os.getenv('VIRTUAL_ENV'):
        print('(releng-tool) not in a virtual environment')
        return

    if hasattr(site, 'getsitepackages'):
        return

    module_path = site.__file__
    if module_path.endswith('pyc'):
        module_path = module_path[:-1]

    print('(releng-tool) updating venv site module to support getsitepackages')

    with open(module_path, 'a') as f:
        # Note: this implementation was taken from Python's `site` module.
        f.write('''
def getsitepackages(prefixes=None):
    if prefixes is None:
        prefixes = PREFIXES

    pkgs = []
    seen = set()

    if prefixes is None:
        prefixes = PREFIXES

    for prefix in prefixes:
        if not prefix or prefix in seen:
            continue
        seen.add(prefix)

        if os.sep == '/':
            platlibdir = getattr(sys, 'platlibdir', 'lib')
            libdirs = [platlibdir]
            if platlibdir != 'lib':
                libdirs.append('lib')

            for libdir in libdirs:
                path = os.path.join(
                    prefix, libdir,
                    'python%d.%d' % sys.version_info[:2],
                    'site-packages',
                )
                pkgs.append(path)
        else:
            pkgs.append(prefix)
            pkgs.append(os.path.join(prefix, 'Lib', 'site-packages'))

    return pkgs
''')


if __name__ == '__main__':
    main()
