# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from io import StringIO
from releng_tool.defs import Rpk
from releng_tool.packages import pkg_key
from releng_tool.util.log import debug
from releng_tool.util.log import is_colorized
from releng_tool.util.log import log
from releng_tool.util.log import success
import ast
import tokenize


def lint(pkgs):
    """
    request to lint project/package and output information to the output stream

    Provides a development helper to attempt to lint the project's or an
    individual package's configuration for quality issues. For any issues
    detected, this information will be provided to the output stream.

    Args:
        pkgs: the package names to print

    Returns:
        ``True`` if no linting issues; ``False`` otherwise
    """

    issue_count = 0

    # populate applicable package keys
    pkgkey_suffixes = tuple(
        f'_{v}' for k, v in Rpk.__dict__.items() if not k.startswith('_')
    )

    for pkg in pkgs:
        # ignore defless packages
        if not pkg.def_file.is_file():
            continue

        debug(f'linting file: {pkg.def_file}')

        # compile a list of supported package options
        supported_pkg_opts = set()
        for k, v in sorted(Rpk.__dict__.items()):
            if k.startswith('_'):
                continue
            supported_pkg_opts.add(pkg_key(pkg.name, v))

        lines_to_ignore = set()

        with pkg.def_file.open() as f:
            def_contents = f.read()

            # populate any noqa line entries if a user wants to ignore a
            # linting rule
            readline_call = StringIO(def_contents).readline
            try:
                for tkn in tokenize.generate_tokens(readline_call):
                    if tkn.type == tokenize.COMMENT and 'noqa' in tkn.string:
                        lines_to_ignore.add(tkn.start[0])
            except tokenize.TokenError:
                pass

            # parse the package definition
            tree = ast.parse(def_contents)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    # ignore line if noqa is set
                    if node.lineno in lines_to_ignore:
                        continue

                    # only check assignments/left-side -- as users may try
                    # to use configuration hints from other packages to
                    # configure options of another package
                    if not isinstance(node.ctx, ast.Store):
                        continue

                    # if this node matches a support configuration key, move
                    # onto the next
                    if node.id in supported_pkg_opts:
                        continue

                    node_flagged = False

                    # check if this variable is named with a suffix matching
                    # known package configuration suffixes; if so, check the
                    # variable does match an expected package key -- if it
                    # does not, most likely an invalid key entry:
                    #  LIBFOOO_VERSION -> LIBFOO_VERSION
                    for suffix in pkgkey_suffixes:
                        if not node.id.endswith(suffix):
                            continue

                        if node.id in supported_pkg_opts:
                            continue

                        _report(
                            0,
                            f'unexpected package configuration: {node.id}',
                            pkg.def_file,
                            node.lineno,
                            node.col_offset,
                        )

                        node_flagged = True
                        issue_count += 1
                        break

                    if node_flagged:
                        continue

                    # check if a supported package option is a subset of this
                    # node identifier:
                    #  LIBFOO_VERSIONN -> LIBFOO_VERSION
                    for supported_pkg_opt in supported_pkg_opts:
                        if supported_pkg_opt in node.id:
                            _report(
                                0,
                                f'unexpected package configuration: {node.id}',
                                pkg.def_file,
                                node.lineno,
                                node.col_offset,
                            )

                            issue_count += 1
                            break

    # if we have no issues, report a success state
    if issue_count == 0:
        success('no detected issues')
        debug('... but who knows what was missed')
    elif issue_count == 1:
        log('Found 1 error.')
    else:
        log(f'Found {issue_count} errors.')

    return issue_count == 0


def _report(code: int, msg: str, path: str, line: int, col: int):
    """
    report a linter issue

    Helps format and print a linter message to a user.

    Args:
        code: the specific lint code
        msg: the message to print
        path: the path of the error
        line: the line in the path
        col: the character column in the line
    """

    code_prefix = '\033[1;31m' if is_colorized() else ''
    code_suffix = '\033[0m' if is_colorized() else ''

    log(f'''\
{code_prefix}RT{code:03d}{code_suffix} {msg}
  --> {path}:{line}:{col}''')
