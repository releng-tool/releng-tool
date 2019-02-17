#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from . import __version__ as releng_version
from .engine import RelengEngine
from .opts import RelengEngineOptions
from .util.log import *
import argparse
import os
import sys

def main():
    """
    mainline

    The mainline for the releng tool.

    Returns:
        the exit code
    """
    retval = 1

    try:
        parser = argparse.ArgumentParser(
            prog='releng', add_help=False, usage=usage())

        parser.add_argument('action', nargs='?')
        parser.add_argument('--cache-dir')
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--development', '-D', action='store_true')
        parser.add_argument('--dl-dir')
        parser.add_argument('--help', '-h', action='store_true')
        parser.add_argument('--jobs', '-j', default=0, type=type_nonnegativeint)
        parser.add_argument('--local-sources', action='store_true')
        parser.add_argument('--nocolorout', action='store_true')
        parser.add_argument('--out-dir')
        parser.add_argument('--root-dir')
        parser.add_argument('--verbose', '-V', action='store_true')
        parser.add_argument('--version', action='version',
            version='%(prog)s ' + releng_version)

        args, unknown_args = parser.parse_known_args()
        if args.help:
            print(usage())
            sys.exit(0)

        # force verbose messages if debugging is enabled
        if args.debug:
            args.verbose = True

        releng_log_configuration(args.debug, args.nocolorout, args.verbose)

        if unknown_args:
            warn('unknown arguments: {}', ' '.join(unknown_args))

        # toggle on ansi colors by default for commands
        if not args.nocolorout:
            os.environ['CLICOLOR_FORCE'] = '1'

        # warn if the *nix-based system is running as root; ill-formed projects
        # may attempt to modify the local system's root
        if sys.platform != 'win32' and os.geteuid() == 0:
            warn('running as root; this may be unsafe')

        # prepare engine options
        opts = RelengEngineOptions(args)

        # register the project's root directory as a system path; permits a
        # project to import locally created modules in their build/etc. scripts
        sys.path.append(opts.root_dir)

        # create and start the engine
        engine = RelengEngine(opts)
        if engine.run():
            retval = 0
    except KeyboardInterrupt:
        print('')
        pass

    return retval

def type_nonnegativeint(value):
    """
    argparse type check for a non-negative integer

    Provides a type check for an argparse-provided argument value to ensure the
    value is a non-negative integer value.

    Args:
        value: the value to check

    Returns:
        the non-negative integer value

    Raises:
        argparse.ArgumentTypeError: detected an invalid non-negative value
    """
    val = int(value)
    if val < 0:
        raise argparse.ArgumentTypeError('invalid non-negative value')
    return val

def usage():
    """
    display the usage for this tool

    Returns a command line usage string for all options available by the releng
    tool.

    Returns:
        the usage string
    """
    return """releng <options> [action]

(actions)
 clean                     clean the output directory
 extract                   extract all packages
 fetch                     fetch all packages
 licenses                  generate license information for a project
 mrproper                  pristine clean of the releng project
 patch                     ensure all packages have done a patch stage
 <pkg>-build               perform build stage for the package
 <pkg>-clean               clean build directory for package
 <pkg>-configure           perform configure stage for the package
 <pkg>-extract             perform extract stage for the package
 <pkg>-fetch               perform fetch stage for the package
 <pkg>-install             perform install stage for the package
 <pkg>-patch               perform patch stage for the package
 <pkg>-rebuild             force a re-build of a specific package
 <pkg>-reconfigure         force a re-configure of a specific package
 <pkg>-reinstall           force a re-install of a specific package

(common options)
 --cache-dir <dir>         directory for vcs-cache (default: <ROOT>/cache)
 --dl-dir <dir>            directory for download archives (default: <ROOT>/dl)
 -j, --jobs <jobs>         numbers of jobs to handle (default: 0; automatic)
 --out-dir <dir>           directory for output (builds, images, etc.)
                            (default: <ROOT>/output)
 --root-dir <dir>          directory to process a releng project
                            (default: working directory)

(mode options)
 -D, --development         enable development mode
 --local-sources           use development sources from a local path

(other)
 --debug                   show debug-related messages
 -h, --help                show this help
 --nocolorout              explicitly disable colorized output
 -V, --verbose             show additional messages
"""

if __name__ == '__main__':
    sys.exit(main())
