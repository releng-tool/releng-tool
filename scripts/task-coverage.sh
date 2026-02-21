#!/usr/bin/env bash
#
# This is a helper script used to invoke all tests that should be passing
# for a changeset and required for a release.

set -e
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null && pwd)
root_dir=$(realpath "$script_dir/../")

perform_cifs_db_tweak=false
perform_clean=true
perform_report=true
new_args=()
for arg in "$@"; do
    case "$arg" in
    --cifs)
        perform_cifs_db_tweak=true
        ;;
    --no-clean)
        perform_clean=false
        ;;
    --no-report)
        perform_report=false
        ;;
    *)
        new_args+=("$arg")
        ;;
    esac
done

cmd_prefix=
if command -v winpty >/dev/null 2>/dev/null; then
    cmd_prefix=winpty
fi

# check if we want to configure a custom database path to prevent sqlite
# issues on a cifs store
if [ $perform_cifs_db_tweak = true ]; then
    printf "Setting up a CIFS database path tweak... "
    mkdir -p /tmp/releng-tool-coverage
    export CUSTOM_COVERAGE_DB=/tmp/releng-tool-coverage/.coverage
    echo "done."
fi

# start with a clean state
if [ $perform_clean = true ]; then
    echo "Cleaning coverage data..."
    $cmd_prefix tox "${new_args[@]}" \
        -c "$script_dir"/../tox-coverage.ini -e coverage-erase
fi

# gather coverage data
echo "Generating coverage data..."
$cmd_prefix tox "${new_args[@]}" \
    -c "$script_dir"/../tox-coverage.ini -e coverage-data

# generate a coverage report
if [ $perform_report = true ]; then
    echo "Building a coverage report..."
    $cmd_prefix tox "${new_args[@]}" \
        -c "$script_dir"/../tox-coverage.ini -e coverage-report
fi

# if we were operating in a cifs mode, relocate the database back to the
# expected location
if [ $perform_cifs_db_tweak = true ]; then
    printf "Copying over coverage database back to CIFS mount... "
    cp "${CUSTOM_COVERAGE_DB%/*}/".* "$root_dir"
    echo "done."
fi
