#!/usr/bin/env bash
#
# This is a helper script used to invoke a all tox tests with a container.

set -e
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null && pwd)
root_dir=$(realpath "$script_dir"/..)
launch_script="$root_dir/support/test-container/launch"

# launch container with the coverage task, starting with a clean state
exec "$launch_script" -- \
    /mnt/scripts/task-full-check.sh \
        --workdir /tmp \
        "$@"
