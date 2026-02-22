#!/usr/bin/env false
# shellcheck shell=sh
#
# This script is to be used with various tox helper scripts (e.g. lint) to
# help automatically detect a CIFS mounted platform. If one is detected, it
# will hint at another tox working directory to use.

[ -n "$RELENG_TOOL_NO_CIFS_CHANGE" ] && return
[ -n "$TOX_WORKDIR" ] && return

fs_type=$(findmnt -T . -o FSTYPE 2>/dev/null | tail -n 1 2>/dev/null)
if [ "$fs_type" = "cifs" ]; then
    export TOX_WORKDIR=~/toxout/releng-tool/
    echo "Detected CIFS; adjusting tox workdir: $TOX_WORKDIR"
fi
