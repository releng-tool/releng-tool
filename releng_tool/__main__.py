# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool import __version__ as releng_version
from releng_tool.engine import RelengEngine
from releng_tool.exceptions import RelengToolException
from releng_tool.opts import RelengEngineOptions
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import releng_log_configuration
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.win32 import enable_ansi as enable_ansi_win32
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
            prog='releng-tool', add_help=False, usage=usage())

        parser.add_argument('action', nargs='?')
        parser.add_argument('--assets-dir')
        parser.add_argument('--cache-dir')
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--development', '-D', action='store_true')
        parser.add_argument('--dl-dir')
        parser.add_argument('--force', '-F', action='store_true')
        parser.add_argument('--help', '-h', action='store_true')
        parser.add_argument('--help-quirks', action='store_true')
        parser.add_argument('--jobs', '-j', default=0, type=type_nonnegativeint)
        parser.add_argument('--local-sources', action='store_true')
        parser.add_argument('--nocolorout', action='store_true')
        parser.add_argument('--out-dir')
        parser.add_argument('--root-dir')
        parser.add_argument('--quirk', action='append')
        parser.add_argument('--verbose', '-V', action='store_true')
        parser.add_argument('--version', action='version',
            version='%(prog)s ' + releng_version)

        known_args = sys.argv[1:]
        forward_args = []
        idx = known_args.index('--') if '--' in known_args else -1
        if idx != -1:
            forward_args = known_args[idx + 1:]
            known_args = known_args[:idx]

        args, unknown_args = parser.parse_known_args(known_args)
        if args.help:
            print(usage())
            sys.exit(0)
        if args.help_quirks:
            print(usage_quirks())
            sys.exit(0)

        # force verbose messages if debugging is enabled
        if args.debug:
            args.verbose = True

        releng_log_configuration(args.debug, args.nocolorout, args.verbose)

        # toggle on ansi colors by default for commands
        if not args.nocolorout:
            os.environ['CLICOLOR_FORCE'] = '1'

            # support character sequences (for color output on win32 cmd)
            if sys.platform == 'win32':
                enable_ansi_win32()

        verbose('releng-tool {}', releng_version)

        if unknown_args:
            warn('unknown arguments: {}', ' '.join(unknown_args))

        if forward_args:
            debug('forwarded arguments: {}', ' '.join(forward_args))

        # warn if the *nix-based system is running as root; ill-formed projects
        # may attempt to modify the local system's root
        if sys.platform != 'win32':
            if os.geteuid() == 0: # pylint: disable=E1101
                if 'RELENG_IGNORE_RUNNING_AS_ROOT' not in os.environ:
                    warn('running as root; this may be unsafe')

        # prepare engine options
        opts = RelengEngineOptions(args=args, forward_args=forward_args)

        # create and start the engine
        engine = RelengEngine(opts)
        try:
            if engine.run():
                retval = 0
        except RelengToolException as e:
            err(e)
    except KeyboardInterrupt:
        print('')

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
    return """releng-tool <options> [action]

(actions)
 clean                     clean the output directory
 distclean                 pristine clean including cache/download content
 extract                   extract all packages
 fetch                     fetch all packages
 init                      initialize a root with an example structure
 licenses                  generate license information for a project
 mrproper                  pristine clean of the releng project
 patch                     ensure all packages have done a patch stage
 <pkg>-build               perform build stage for the package
 <pkg>-clean               clean build directory for package
 <pkg>-configure           perform configure stage for the package
 <pkg>-distclean           pristine clean for package
 <pkg>-extract             perform extract stage for the package
 <pkg>-fetch               perform fetch stage for the package
 <pkg>-install             perform install stage for the package
 <pkg>-license             generate license information for the package
 <pkg>-patch               perform patch stage for the package
 <pkg>-rebuild             force a re-build of a specific package
 <pkg>-rebuild-only        force a re-build of a specific package and stop
 <pkg>-reconfigure         force a re-configure of a specific package
 <pkg>-reconfigure-only    force a re-configure of a specific package and stop
 <pkg>-reinstall           force a re-install of a specific package

(common options)
 --assets-dir <dir>        container directory for download and vcs-cache
                            directories (e.g. <ASSETS_DIR>/cache)
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
 -F, --force               trigger a forced request
 -h, --help                show this help
 --help-quirks             show available quirks
 --nocolorout              explicitly disable colorized output
 --quirk <value>           inject in quirk into this run
 -V, --verbose             show additional messages
 --version                 show the version
"""

def usage_quirks():
    """
    display the available quirks in this tool

    Returns a string of available quirks in this tool.

    Returns:
        the quirks string
    """
    return """releng-tool quirks

releng.cmake.disable_parallel_option   disable parallel cmake
releng.disable_prerequisites_check     disable prerequisites check
releng.disable_remote_configs          disable remote configurations
releng.disable_remote_scripts          disable remote scripts
releng.git.no_depth                    disable depth-limits for git calls
releng.git.no_quick_fetch              disable quick-fetching for git calls
"""

if __name__ == '__main__':
    sys.exit(main())
