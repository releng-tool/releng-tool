# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool import __version__ as releng_version
from releng_tool.defs import SbomFormatType
from releng_tool.engine import RelengEngine
from releng_tool.exceptions import RelengToolException
from releng_tool.exceptions import RelengToolSilentException
from releng_tool.opts import RelengEngineOptions
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import releng_log_configuration
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.runner import detect_ci_runner_debug_mode
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
        parser.add_argument('--debug-extended', action='store_true')
        parser.add_argument('--development', '-D', nargs='?', default=False)
        parser.add_argument('--dl-dir')
        parser.add_argument('--force', '-F', action='store_true')
        parser.add_argument('--help', '-h', action='store_true')
        parser.add_argument('--help-quirks', action='store_true')
        parser.add_argument('--images-dir')
        parser.add_argument('--jobs', '-j', default=0, type=type_nonnegativeint)
        parser.add_argument('--local-sources', '-L', nargs='?', action='append')
        parser.add_argument('--nocolorout', action='store_true')
        parser.add_argument('--only-mirror', action='store_true')
        parser.add_argument('--out-dir')
        parser.add_argument('--profile', '-P', action='append')
        parser.add_argument('--relaxed-args', action='store_true')
        parser.add_argument('--root-dir')
        parser.add_argument('--sbom-format', type=type_sbom_format)
        parser.add_argument('--quirk', action='append')
        parser.add_argument('--verbose', '-V', action='store_true')
        parser.add_argument('--version', action='version',
            version='%(prog)s ' + releng_version)
        parser.add_argument('--werror', '-Werror', action='store_true')

        # hidden convenience argument -- we officially promote the use of
        # `--out-dir`, but to help a user who may accidentally use the
        # argument `--output-dir`, we want to help avoid them from generating
        # output into an root location
        parser.add_argument('--output-dir')

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

        # if a CI debug mode (e.g. GitHub "debug" runs) is detected,
        # automatically enable debugging for releng-tool
        if not os.getenv('RELENG_IGNORE_RUNNER_DEBUG'):
            if detect_ci_runner_debug_mode():
                args.debug = True

        # force debug messages if extended debugging is enabled
        if args.debug_extended:
            args.debug = True

        # force verbose messages if debugging is enabled
        if args.debug:
            args.verbose = True

        # force color off if `NO_COLOR` is configured
        if os.getenv('NO_COLOR'):
            args.nocolorout = True

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

        # show banner unless we are processing a specific action, since some
        # actions may have no output and it looks weird to just print the
        # version out
        show_banner = not args.action
        if show_banner:
            log('releng-tool {}', releng_version)

        # register any injected entry into the working environment right away
        for k, v in args.injected_kv.items():
            os.environ[k] = v

        if 'RELENG_IGNORE_UNKNOWN_ARGS' not in os.environ and unknown_args:
            unknown_msg = err if not args.relaxed_args else warnerr
            unknown_msg('unknown arguments: {}', ' '.join(unknown_args))
            if not args.relaxed_args or args.werror:
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
                    except OSError:
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
        except RelengToolSilentException:
            pass
        except RelengToolException as e:
            err(e)
    except KeyboardInterrupt:
        print()

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
            continue

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


def type_sbom_format(value):
    """
    argparse type check for sbom format types

    Provides a type check for an argparse-provided argument value to ensure the
    value is accept SBOM formats.

    Args:
        value: the value to check

    Returns:
        the sbom format(s)

    Raises:
        argparse.ArgumentTypeError: detected an invalid sbom format is provided
    """

    values = list(set(value.split(',')))

    for entry in values:
        if entry not in SbomFormatType:
            raise argparse.ArgumentTypeError('invalid format provided')

    return values


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
 clean                     Clean the output directory
 distclean                 Pristine clean including cache/download content
 extract                   Extract all packages
 fetch                     Fetch all packages
 fetch-full                Fetch all packages including post-fetch dependencies
 init                      Initialize a root with an example structure
 licenses                  Generate license information for a project
 mrproper                  Pristine clean of the releng project
 patch                     Ensure all packages have done a patch stage
 punch                     Full run with a forced re-run on all packages
 sbom                      Generate a software bill of materials
 <pkg>                     Perform all stages for the package
 <pkg>-build               Perform build stage for the package
 <pkg>-clean               Clean build directory for package
 <pkg>-configure           Perform configure stage for the package
 <pkg>-distclean           Pristine clean for package
 <pkg>-exec <cmd>          Invoke a command in the package's directory
 <pkg>-extract             Perform extract stage for the package
 <pkg>-fetch               Perform fetch stage for the package
 <pkg>-fetch-full          Perform fetch stage for the package (with post-fetch)
 <pkg>-fresh               Freshly prepare a package output
 <pkg>-install             Perform install stage for the package
 <pkg>-license             Generate license information for the package
 <pkg>-patch               Perform patch stage for the package
 <pkg>-rebuild             Force a re-build of a specific package
 <pkg>-rebuild-only        Force a re-build of a specific package and stop
 <pkg>-reconfigure         Force a re-configure of a specific package
 <pkg>-reconfigure-only    Force a re-configure of a specific package and stop
 <pkg>-reinstall           Force a re-install of a specific package

(options)
 --assets-dir <dir>        Container directory for download and VCS-cache
                            directories (e.g. <ASSETS_DIR>/cache)
 --cache-dir <dir>         Directory for VCS-cache (default: <ROOT>/cache)
 --config <file>           Configuration to use (default: <ROOT>/releng-tool.rt)
 --development [<mode>], -D [<mode>]
                           Enable development mode
 --debug                   Show debug-related messages
 --debug-extended          Show even more debug-related messages
 --dl-dir <dir>            Directory for download archives (default: <ROOT>/dl)
 --force, -F               Trigger a forced request
 --help, -h                Show this help
 --help-quirks             Show available quirks
 --images-dir <dir>        Directory for generated images
                            (default: <ROOT>/output/images)
 --jobs <jobs>, -j <jobs>  Numbers of jobs to handle (default: 0; automatic)
                            (default: working directory)
 --local-sources [[<pkg>:]<dir>], -L [[<pkg>:]<dir>]
                           Use development sources from a local path, defaults
                            to the parent of the root directory; users can use
                            the format "<pkg>:<path>" to set/override specific
                            local paths per package; this argument can be
                            provided multiple times
 --nocolorout              Explicitly disable colorized output
 --only-mirror             Only fetch external projects with configured mirror
 --out-dir <dir>           Directory for output (builds, images, etc.)
                            (default: <ROOT>/output)
 --profile <profile>, -D <profile>
                           Configure a profile to run with; providing this
                            option is only applicable if the project accepts
                            custom profile options; multiple profiles can be
                            provided by repeating this argument
 --quirk <value>           Inject in quirk into this run
 --relaxed-args            Permit the use of unknown arguments
 --root-dir <dir>          Directory to process a releng project
 --sbom-format <format>    Override the output format for a software build of
                            materials (e.g. csv, json)
 --verbose, -V             Show additional messages
 --version                 Show the version
 --werror, -Werror         Treat warnings as errors

Using only "--" as an argument can forward remaining arguments into a
<pkg>-exec invoke or into the releng-tool project (if configured to accept).

For more help on using releng-tool, head to: https://docs.releng.io
"""


def usage_quirks():
    """
    display the available quirks in this tool

    Returns a string of available quirks in this tool.

    Returns:
        the quirks string
    """
    return """releng-tool quirks

releng.bzr.certifi                     Use certifi for bzr exports
releng.cmake.disable_direct_includes   Disable include-injection with CMake
releng.disable_devmode_ignore_cache    Disable package ignore-cache flags
releng.disable_prerequisites_check     Disable prerequisites check
releng.disable_remote_configs          Disable remote configurations
releng.disable_remote_scripts          Disable remote scripts
releng.disable_spdx_check              Disable SPDX license checks
releng.disable_verbose_patch           Disable use of --verbose in patch calls
releng.git.no_depth                    Disable depth-limits for Git calls
releng.git.no_quick_fetch              Disable quick-fetching for Git calls
releng.git.replicate_cache             Copy Git repositories into build outputs
releng.log.execute_args                Enable execute argument line logging
releng.log.execute_env                 Enable execute envrionment debug logging
releng.stats.no_pdf                    Never generate PDF statistics output
"""


if __name__ == '__main__':
    sys.exit(main())
