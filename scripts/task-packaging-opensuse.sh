#!/usr/bin/env bash
#
# This is a helper script used to test packaging for openSUSE.

set -e
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null && pwd)
root_dir=$(realpath "$script_dir"/..)
launch_script="$root_dir/support/test-container/launch"
image="$root_dir/support/test-container/Dockerfile-opensuse"

# launch container
exec "$launch_script" "$image" \
    --mount type=tmpfs,destination=/mnt/build,tmpfs-mode=1777 \
    --mount type=tmpfs,destination=/mnt/dist,tmpfs-mode=1777 \
    --mount type=tmpfs,destination=/mnt/releng_tool.egg-info,tmpfs-mode=1777 \
    -- \
    bash -c "
    set -e;
    cd /mnt;
    python3 -m build --wheel --no-isolation;
	python3 -m venv --clear --without-pip --system-site-packages /tmp/.testenv
	python3 -m installer --prefix /tmp/.testenv dist/*.whl;
	python3 -Wd -m tests;
    export RELENG_SKIP_TEST_TOOL_BREEZY=1
    export RELENG_SKIP_TEST_TOOL_PYTHON_PDM=1
    export RELENG_SKIP_TEST_TOOL_PYTHON_PDM_LEGACY=1
    export RELENG_SKIP_TEST_TOOL_PYTHON_POETRY=1
    export RELENG_SKIP_TEST_TOOL_WAF=1
    export RELENG_SKIP_TEST_TOOL_XMAKE=1
	python3 -Wd -m tests --test-dir tool-tests;
    "
