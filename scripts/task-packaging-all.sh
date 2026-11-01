#!/usr/bin/env bash
#
# This is a helper script used to test packaging for all supported platforms.

set -e

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null && pwd)

pull_images=false
for arg in "$@"; do
    case "$arg" in
    --pull)
        pull_images=true
        ;;
    esac
done

if [ $pull_images = true ]; then
    echo "Pulling latest images..."
    docker pull alpine
    docker pull archlinux
    docker pull debian
    docker pull fedora
    docker pull opensuse/leap
    docker pull ubuntu
fi

"$script_dir"/task-packaging-alpine.sh
"$script_dir"/task-packaging-archlinux.sh
"$script_dir"/task-packaging-debian.sh
"$script_dir"/task-packaging-fedora.sh
"$script_dir"/task-packaging-opensuse.sh
"$script_dir"/task-packaging-ubuntu.sh
