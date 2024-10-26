#!/usr/bin/env sh

exec tox -c tox-release.ini -e prepare-release
