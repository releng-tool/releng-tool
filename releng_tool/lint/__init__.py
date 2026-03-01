# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from collections.abc import Iterator
from io import StringIO
from pathlib import Path
from releng_tool.defs import Rpk
from releng_tool.opts import RelengEngineOptions
from releng_tool.packages import pkg_key
from releng_tool.packages.package import RelengPackage
from releng_tool.util.log import debug
from releng_tool.util.log import is_colorized
from releng_tool.util.log import log
from releng_tool.util.log import success
import ast
import tokenize


class LintState:
    def __init__(self):
        """
        track the state of a lint event

        Attributes:
            pkgkey_suffixes: populated list of all package key suffixes
            pkgkey_opts: cached possible package keys
            issue_count: total number of issues detected
        """

        # populate package key suffixes
        self.pkgkey_suffixes = tuple(
            f'_{v}' for k, v in Rpk.__dict__.items() if not k.startswith('_')
        )

        # cache of package keys
        self.pkgkey_opts = {}

        # track total issues detected
        self.issue_count = 0

    def report(self, code: int, path: str, node: ast.expr | ast.stmt, msg: str,
            extra: str = ''):
        """
        report a linter issue

        Helps format and print a linter message to a user.

        Args:
            code: the specific lint code
            path: the path of the error
            node: the node related to this report
            msg: the message to print
            extra (optional): extra text to append
        """

        code_prefix = '\033[1;31m' if is_colorized() else ''
        code_suffix = '\033[0m' if is_colorized() else ''

        log(f'''\
{code_prefix}RT{code:03d}{code_suffix} {msg}
  --> {path}:{node.lineno}:{node.col_offset}
{extra}''')

        # increment the detected issue event
        self.issue_count += 1

    def finalize(self):
        """
        finalize the linting event

        This call finalizes the linting event by reporting to a user the
        success/fail state.

        Returns:
            whether any issues were detected
        """

        # if we have no issues, report a success state
        if self.issue_count == 0:
            success('no detected issues')
            debug('... but who knows what was missed')
        elif self.issue_count == 1:
            log('Found 1 error.')
        else:
            log(f'Found {self.issue_count} errors.')

        return self.issue_count == 0


def lint(opts: RelengEngineOptions, pkgs: list[RelengPackage]) -> bool:
    """
    request to lint project/package and output information to the output stream

    Provides a development helper to attempt to lint the project's or an
    individual package's configuration for quality issues. For any issues
    detected, this information will be provided to the output stream.

    Args:
        opts: runtime options
        pkgs: the package names to print

    Returns:
        ``True`` if no linting issues; ``False`` otherwise
    """

    # ruff: noqa: PLC0415
    from releng_tool.lint.rt100 import rt100
    from releng_tool.lint.rt101 import rt101
    from releng_tool.lint.rt102 import rt102

    state = LintState()

    for pkg in pkgs:
        # ignore defless packages
        if not pkg.def_file.is_file():
            continue

        debug(f'linting file: {pkg.def_file}')

        # compile a list of supported package options
        state.pkgkey_opts[pkg] = set()
        for k, v in sorted(Rpk.__dict__.items()):
            if k.startswith('_'):
                continue
            state.pkgkey_opts[pkg].add(pkg_key(pkg.name, v))

        nodes = list(process_nodes(pkg.def_file))
        for node in nodes:
            rt100(state, pkg, node)
            rt101(state, opts, pkg, node)

        rt102(state, pkg, nodes)
    return state.finalize()


def process_nodes(path: Path) -> Iterator[ast.AST]:
    """
    process nodes from a file

    Process and return detected nodes found in the file. Nodes detected to
    be flagged for noqa are ignored and skipped over.

    Args:
        path: the file to process

    Returns:
        a detected nodes
    """

    lines_to_ignore = compile_lines_to_ignore(path)

    with path.open() as f:
        contents = f.read()

        tree = ast.parse(contents)
        for node in ast.walk(tree):
            if isinstance(node, (ast.expr, ast.stmt)):
                # ignore line if noqa is set
                if node.lineno in lines_to_ignore:
                    continue

            yield node


def compile_lines_to_ignore(path: Path) -> set[int]:
    """
    compile lines of a file to ignore

    Process a file for known lines that should be ignored from linting checks.
    This call scans for comments that include a ``noqa`` hint and return all
    known lines in a set.

    Args:
        path: the file to process

    Returns:
        set of lines to ignore
    """

    lines_to_ignore: set[int] = set()

    with path.open() as f:
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

    return lines_to_ignore
