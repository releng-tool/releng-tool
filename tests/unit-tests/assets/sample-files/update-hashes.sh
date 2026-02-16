#!/usr/bin/env bash
#
# This is a helper script used to only invoke a subset of test environments
# associated to linting.

for f in sample-files*; do
    [[ "$f" == *.hash ]] && continue
    hash=$(sha1sum "$f")
    hash=${hash/\*}
    echo "sha1 $hash" >"$f.hash"
done
