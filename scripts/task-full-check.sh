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

# invoke environments that can run with modern tox
primary_envs=(
    ruff
    pylint
    py37
    py38
    py39
    py310
    py311
    py312
    py313
    py314
    pypy3
    py37-tools
    py38-tools
    py39-tools
    py310-tools
    py311-tools
    py312-tools
    py313-tools
    py314-tools
    py37-release
    py38-release
    py39-release
    py310-release
    py311-release
    py312-release
    py313-release
    py314-release
)

envs=$(IFS=, ; echo "${primary_envs[*]}")
$cmd_prefix tox -p -e "$envs" "$@"

# invoke legacy environments with an older version of tox
legacy_envs=(
    py34
    py35
    py36
    pypy2
    py27-tools
    py34-tools
    py35-tools
    py36-tools
    py27-release
    py34-release
    py35-release
    py36-release
)

envs=$(IFS=, ; echo "${legacy_envs[*]}")
$cmd_prefix "$SHELL" \
    "$script_dir/tox-legacy.sh" \
    -p "$(nproc)" \
    -e "$envs" \
    --skip-missing-interpreters

# invoke py27 manually, since running inside an environment set will cause
# issues with loading extension tests in an older py27-venv setup
$cmd_prefix "$SHELL" \
    "$script_dir/tox-legacy.sh" \
    -p "$(nproc)" \
    -e py27 "$@"
