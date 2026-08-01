#!/usr/bin/env bash
#
# This is a helper script used to test packaging for Arch Linux.

set -e
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null && pwd)
root_dir=$(realpath "$script_dir"/..)
launch_script="$root_dir/support/test-container/launch"
image="$root_dir/support/test-container/Dockerfile-archlinux"

# launch container
exec "$launch_script" "$image" \
    --mount type=tmpfs,destination=/mnt/build,tmpfs-mode=1777 \
    --mount type=tmpfs,destination=/mnt/dist,tmpfs-mode=1777 \
    --mount type=tmpfs,destination=/mnt/releng_tool.egg-info,tmpfs-mode=1777 \
    -- \
    bash -c "
    set -e;
    cd /mnt;
    python -m build --wheel --no-isolation;
	python -m venv --clear --without-pip --system-site-packages /tmp/.testenv
	python -m installer --prefix /tmp/.testenv dist/*.whl;
	python -Wd -m tests;
    export RELENG_SKIP_TEST_TOOL_PYTHON_PDM=1;
    export RELENG_SKIP_TEST_TOOL_PYTHON_PDM_LEGACY=1;
	python -Wd -m tests --test-dir tool-tests;
    "
