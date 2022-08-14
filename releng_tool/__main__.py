# -*- coding: utf-8 -*-
# Copyright 2018-2022 releng-tool

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

        parser.add_argument('--assets-dir')
        parser.add_argument('--cache-dir')
        parser.add_argument('--config')
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--development', '-D', nargs='?', default=False)
        parser.add_argument('--dl-dir')
        parser.add_argument('--force', '-F', action='store_true')
        parser.add_argument('--help', '-h', action='store_true')
        parser.add_argument('--help-quirks', action='store_true')
        parser.add_argument('--images-dir')
        parser.add_argument('--jobs', '-j', default=0, type=type_nonnegativeint)
        parser.add_argument('--local-sources', '-L', nargs='?', action='append')
        parser.add_argument('--nocolorout', action='store_true')
        parser.add_argument('--out-dir')
        parser.add_argument('--root-dir')
        parser.add_argument('--quirk', action='append')
        parser.add_argument('--verbose', '-V', action='store_true')
        parser.add_argument('--version', action='version',
            version='%(prog)s ' + releng_version)
        parser.add_argument('--werror', '-Werror', action='store_true')

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

        # handle a `None` value being a "True" state; and a (default) `False`
        # value being an unset (`None`) state
        if args.development is not False:
            args.development = args.development if args.development else True
        else:
            args.development = None

        # force verbose messages if debugging is enabled
        if args.debug:
            args.verbose = True

        releng_log_configuration(
            args.debug, args.nocolorout, args.verbose, args.werror)

        warnerr = err if args.werror else warn

        # toggle on ansi colors by default for commands
        if not args.nocolorout:
            os.environ['CLICOLOR_FORCE'] = '1'

            # support character sequences (for color output on win32 cmd)
            if sys.platform == 'win32':
                enable_ansi_win32()

        verbose('releng-tool {}', releng_version)
        debug('({})', __file__)

        # extract additional argument information:
        #  - pull the action value
        #  - pull "exec" command (if applicable)
        #  - key-value entries to be injected into the running
        #     script/working environment
        new_args, unknown_args = process_args(unknown_args)
        args.action = new_args['action']
        args.action_exec = new_args['exec']
        args.injected_kv = new_args['entries']

        # register any injected entry into the working environment right away
        for k, v in args.injected_kv.items():
            os.environ[k] = v

        if unknown_args:
            warnerr('unknown arguments: {}', ' '.join(unknown_args))
            if args.werror:
                return retval

        if forward_args:
            debug('forwarded arguments: {}', ' '.join(forward_args))

        # warn if the *nix-based system is running as root; ill-formed projects
        # may attempt to modify the local system's root
        if sys.platform != 'win32':
            if os.geteuid() == 0:  # pylint: disable=E1101
                if 'RELENG_IGNORE_RUNNING_AS_ROOT' not in os.environ:
                    # attempt to check if we are in a container; if so, ignore
                    # generating a warning -- we will check if kernel threads
                    # are running on pid2; if not, it is most likely that we
                    # are in a container environment; checks for a container
                    # do not have to be perfect here, only to try to help
                    # improve a user's experience (suppressing this warning
                    # when not running on a typical host setup)
                    try:
                        with open('/proc/2/status') as f:
                            inside_container = 'kthreadd' not in f.read()
                    except IOError:
                        inside_container = True

                    if not inside_container:
                        warnerr('running as root; this may be unsafe')
                        if args.werror:
                            return retval

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

def process_args(args):
    """
    process arguments for an action and key-value entries for environments

    The following will process a remaining argument set for an provided action
    and entries which could be injected into the script/working environment.
    The goal is to support Make-styled variable assignment options from a
    command line, providing users a consistent way to override/set options no
    matter the platform.

    Args:
        args: the arguments to check for entries

    Returns:
        parsed argument options and the remaining/unknown arguments
    """

    action = None
    entries = {}
    exec_ = None
    needs_exec = False
    unknown_args = list(args)

    for arg in args:
        # always ignore option entries
        if arg.startswith('-'):
            continue

        if needs_exec:
            exec_ = arg.strip()
            unknown_args.remove(arg)
            debug('detected package-exec call: {}', exec_)
            needs_exec = False

        is_entry = False
        if '=' in arg:
            key, value = arg.split('=', 1)
            key = key.strip()
            if key:
                is_entry = True
                entries[key] = value.strip()
                unknown_args.remove(arg)
                debug('detected entry: {}={}', key, entries[key])

        # if this argument is not an entry and we haven't yet registered an
        # action yet, consider this argument the action
        if not action and not is_entry:
            action = arg
            unknown_args.remove(arg)
            debug('detected action: {}', action)

            # if this is assumed to be an `exec`-based package action, consume
            # the next non-kv entry as the expected command to invoke
            if action.endswith('-exec'):
                debug('assuming action is an exec call')
                needs_exec = True

    return {
        'action': action,
        'entries': entries,
        'exec': exec_,
    }, unknown_args

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
 <pkg>-exec <cmd>          invoke a command in the package's directory
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
 -L, --local-sources [[<pkg>@]<dir>]
                           use development sources from a local path, defaults
                            to the parent of the root directory; users can use
                            the format "<pkg>@<path>" to set/override specific
                            local paths per package; this argument can be
                            provided multiple times

(other)
 --config <file>           configuration file to load (default: <ROOT>/releng)
 --debug                   show debug-related messages
 -F, --force               trigger a forced request
 -h, --help                show this help
 --help-quirks             show available quirks
 --nocolorout              explicitly disable colorized output
 --quirk <value>           inject in quirk into this run
 -V, --verbose             show additional messages
 --version                 show the version
 --werror, -Werror         treat warnings as errors
"""

def usage_quirks():
    """
    display the available quirks in this tool

    Returns a string of available quirks in this tool.

    Returns:
        the quirks string
    """
    return """releng-tool quirks

releng.bzr.certifi                     use certifi for bzr exports
releng.cmake.disable_parallel_option   disable parallel cmake
releng.disable_prerequisites_check     disable prerequisites check
releng.disable_remote_configs          disable remote configurations
releng.disable_remote_scripts          disable remote scripts
releng.git.no_depth                    disable depth-limits for git calls
releng.git.no_quick_fetch              disable quick-fetching for git calls
"""

if __name__ == '__main__':
    sys.exit(main())
