#!/usr/bin/env bash
#
# This is a helper script used to invoke coverage tests with a container.
# It is designed in a way where the mounted path is from a Windows host,
# allowing it to populate Linux coverage data into the project directory.
# After a run, the Windows host can run a similar coverage check, allowing
# a final report to be made based off the combination of the various host
# types.

set -e
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null && pwd)
root_dir=$(realpath "$script_dir"/..)
launch_script="$root_dir/support/test-container/launch"

# launch container with the coverage task, starting with a clean state
exec "$launch_script" -- \
    /mnt/scripts/task-coverage.sh --no-report --workdir /tmp
