#!/usr/bin/env bash
#
# This is a helper script used to only invoke a subset of default test
# environments for legacy interpreters.

TOX_ENVS="py27,py34,py35,py36,pypy"

args=()
while [ "$#" -gt 0 ]; do
    [[ "$1" == "--" ]] && break
    args+=("$1"); shift
done

has_env=false
for arg in "${args[@]}"; do
    [[ "$arg" == "-e" ]] && has_env=true && break
done

if [ "$has_env" = false ]; then
    args+=("-e")
    args+=("$TOX_ENVS")
fi

if [[ "$(uname)" == "MINGW"*"_NT"* ]]; then
    interpreter="/c/Program Files/Python37/python"
else
    interpreter="python3.7"
fi

exec "$interpreter" -m tox "${args[@]}" "$@"
