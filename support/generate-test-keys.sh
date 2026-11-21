#!/usr/bin/env sh
# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool
#
# This is a helper script used to generate the keys used for unit testing.

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
httpd_dir="$script_dir/../tests/unit-tests/assets/httpd"
httpd_dir=$(realpath --relative-to=. "$httpd_dir")

if [ ! -d "$httpd_dir" ]; then
    echo "unable to find httpd unit test path: $httpd_dir"
    exit 1
fi

export MSYS_NO_PATHCONV=1
exec openssl req \
    -x509 \
    -newkey rsa:2048 \
    -nodes \
    -keyout "$httpd_dir"/test-notprivate-key-pem \
    -out "$httpd_dir"/test-cert-pem \
    -days 36500 \
    -subj "/C=CA/ST=Some-State/O=releng-tool/CN=localhost" \
    -addext "basicConstraints=critical,CA:TRUE" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
