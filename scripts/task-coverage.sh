#!/usr/bin/env bash
#
# This is a helper script used to invoke all tests that should be passing
# for a changeset and required for a release.

set -e
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null && pwd)

cmd_prefix=
if command -v winpty >/dev/null 2>/dev/null; then
    cmd_prefix=winpty
fi

# gather coverage data under Python 2.7
$cmd_prefix "$SHELL" "$script_dir"/tox-legacy.sh \
    -c "$script_dir"/../tox-coverage.ini -e coverage-py27

# gather coverage data under Python 3
$cmd_prefix tox \
    -c "$script_dir"/../tox-coverage.ini -e coverage-py3
