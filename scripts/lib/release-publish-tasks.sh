#!/usr/bin/env bash
#
# A helper script to publish a release to PyPI.

set -e

lib_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
script_dir=$(cd -- "$(dirname -- "$lib_dir")" &>/dev/null && pwd)
root_dir=$(cd -- "$(dirname -- "$script_dir")" &>/dev/null && pwd)
dist_dir="$root_dir/dist"

# Spacer to help separate tox output.
trap 'printf "\n\n"' EXIT
printf "\n\n"

# verify working within a tox-prepared virtual environment
if [ -z "$RELENG_TOOL_PUBLISH_RELEASE" ]; then
    echo "Script has not been invoked through tox."
    exit 1
fi

# find files to upload and verify they exist
echo "Checking for release files..."
readarray -t files <"$dist_dir"/release-files.txt
if [ -z "${files[*]}" ]; then
    echo "No release files detected."
    exit 1
fi

for entry in "${files[@]}"; do
    fname=${entry##*/}
    echo -n "  [$fname] "
    if [ ! -f "$entry" ]; then
        echo "missing"
        exit 1
    fi
    echo "found"
done

# trigger twine upload
echo ""
echo "Starting upload request..."
python -m twine upload --repository releng-tool "${files[@]}"
