#!/usr/bin/env bash
#
# This is a helper script used to test packaging for all supported platforms.

set -e

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null && pwd)

"$script_dir"/task-packaging-alpine.sh
"$script_dir"/task-packaging-archlinux.sh
"$script_dir"/task-packaging-debian.sh
"$script_dir"/task-packaging-fedora.sh
"$script_dir"/task-packaging-opensuse.sh
"$script_dir"/task-packaging-ubuntu.sh
