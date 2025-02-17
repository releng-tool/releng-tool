#!/usr/bin/env bash
#
# A helper script to prepare releng-tool for a release.

set -e

lib_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
script_dir=$(cd -- "$(dirname -- "$lib_dir")" &>/dev/null && pwd)
root_dir=$(cd -- "$(dirname -- "$script_dir")" &>/dev/null && pwd)
dist_dir="$root_dir/dist"

# Spacer to help separate tox output.
trap 'printf "\n\n"' EXIT
printf "\n\n"

# verify working within a tox-prepared virtual environment
if [ -z "$RELENG_TOOL_PREPARE_RELEASE" ]; then
    echo "Script has not been invoked through tox."
    exit 1
fi

# verify working from a clean state
mkdir -p "$dist_dir"
if [ -n "$(ls -A "$dist_dir")" ]; then
    echo "Distribution directory is not empty."
    exit 1
fi

# verify that we are on a tag
echo "Verify release tag..."
tag=$(git describe --tags --abbrev=0 --exact-match 2>/dev/null || true)
if [ -z "$tag" ]; then
    echo "Missing tag on current worktree."
    exit 1
fi
echo "Detected tag: $tag"

git verify-tag "$tag"

# build releng-tool
echo ""
echo "Building package..."
exec 9>&1
out=$(python -m build | tee >(cat - >&9))
success_msg="${out##*Successfully built}"

# detect files and version
echo ""
echo "Populating generated files..."
files=()
for entry in $success_msg; do
    fentry="$dist_dir/$entry"
    if [ -f "$fentry" ]; then
        files+=("$fentry")
    fi
done

if [ ${#files[@]} -eq 0 ]; then
    echo "No files detected."
    exit 1
fi

# determine version
version=
for file in "${files[@]}"; do
    if [[ "$file" == *.tar.gz ]]; then
        fname=${file##*/}
        part="${fname%.tar.gz}"
        version="${part#releng_tool-}"
        break
    fi
done

if [ -z "$version" ]; then
    echo "Unable to detect version."
    exit 1
fi
echo "Detected version: $version"

# twine checks
echo ""
echo "Performing twine check..."
for file in "${files[@]}"; do
    python -m twine check --strict "$file"
done

# gpg signing release files
echo ""
echo "Sign artifacts..."
for file in "${files[@]}"; do
    fname=${file##*/}
    echo "[gpg-sign] $fname"
    gpg --detach-sign --armor --yes "$file"
done

echo ""
echo "Verify artifacts..."
for file in "${files[@]}"; do
    fname=${file##*/}
    echo "[gpg-verify] $fname"
    gpg --verify "${file}.asc"
done

# generate hashes
hash_tools=(
    sha256sum
    sha512sum
)

echo ""
echo "Generating hashes..."
pushd "$dist_dir" >/dev/null
for hash_tool in "${hash_tools[@]}"; do
    rm "releng-tool-$version.$hash_tool" 2>/dev/null || true
    for file in "${files[@]}"; do
        fname=${file##*/}
        echo "[$hash_tool] $fname"
        $hash_tool -b "$fname" >>"releng_tool-$version.$hash_tool"
        echo "[$hash_tool] $fname.asc"
        $hash_tool -b "$fname.asc" >>"releng_tool-$version.$hash_tool"
    done
done
popd >/dev/null

# dump prepare files to a metadata file
metadata_file="$dist_dir/release-files.txt"
rm "$metadata_file" 2>/dev/null || true
for file in "${files[@]}"; do
    fname=${file##*/}
    echo "dist/$fname" >>"$metadata_file"
done

echo ""
echo "Ready for PyPI publish, tag push ($tag) and release entry!"
