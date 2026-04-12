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
    py310
    py311
    py312
    py313
    py314
    pypy3
    py310-tools
    py310-tools-py-flit
    py310-tools-py-flit-old-installer
    py310-tools-py-hatch
    py310-tools-py-hatch-old-installer
    py310-tools-py-pdm
    py310-tools-py-pdm-old-installer
    py310-tools-py-pep517
    py310-tools-py-pep517-old-installer
    py310-tools-py-poetry
    py310-tools-py-poetry-old-installer
    py310-tools-py-setuptools
    py310-tools-py-setuptools-old-installer
    py311-tools
    py311-tools-py-flit
    py311-tools-py-flit-old-installer
    py311-tools-py-hatch
    py311-tools-py-hatch-old-installer
    py311-tools-py-pdm
    py311-tools-py-pdm-old-installer
    py311-tools-py-pep517
    py311-tools-py-pep517-old-installer
    py310-tools-py-poetry
    py310-tools-py-poetry-old-installer
    py311-tools-py-setuptools
    py311-tools-py-setuptools-old-installer
    py312-tools
    py312-tools-py-flit
    py312-tools-py-flit-old-installer
    py312-tools-py-hatch
    py312-tools-py-hatch-old-installer
    py312-tools-py-pdm
    py312-tools-py-pdm-old-installer
    py312-tools-py-pep517
    py312-tools-py-pep517-old-installer
    py312-tools-py-poetry
    py312-tools-py-poetry-old-installer
    py312-tools-py-setuptools
    py312-tools-py-setuptools-old-installer
    py313-tools
    py313-tools-py-flit
    py313-tools-py-flit-old-installer
    py313-tools-py-hatch
    py313-tools-py-hatch-old-installer
    py313-tools-py-pdm
    py313-tools-py-pdm-old-installer
    py313-tools-py-pep517
    py313-tools-py-pep517-old-installer
    py313-tools-py-poetry
    py313-tools-py-poetry-old-installer
    py313-tools-py-setuptools
    py313-tools-py-setuptools-old-installer
    py314-tools
    py314-tools-py-flit
    py314-tools-py-flit-old-installer
    py314-tools-py-hatch
    py314-tools-py-hatch-old-installer
    py314-tools-py-pdm
    py314-tools-py-pdm-old-installer
    py314-tools-py-pep517
    py314-tools-py-pep517-old-installer
    py314-tools-py-poetry
    py314-tools-py-poetry-old-installer
    py314-tools-py-setuptools
    py314-tools-py-setuptools-old-installer
    py310-release
    py311-release
    py312-release
    py313-release
    py314-release
)

envs=$(IFS=, ; echo "${primary_envs[*]}")
exec $cmd_prefix tox -c "$script_dir"/../tox.ini -p -e "$envs" "$@"
