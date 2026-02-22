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

# allow cifs override hint
source "$script_dir"/tox-cifs-workdir.sh

# invoke environments that can run with modern tox
primary_envs=(
    ruff
    pylint
    py39
    py310
    py311
    py312
    py313
    py314
    pypy3
    py39-tools
    py310-tools
    py311-tools
    py312-tools
    py313-tools
    py314-tools
    py39-release
    py310-release
    py311-release
    py312-release
    py313-release
    py314-release
)

envs=$(IFS=, ; echo "${primary_envs[*]}")
$cmd_prefix tox -p -e "$envs" "$@"
