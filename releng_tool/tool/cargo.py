# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool

#: executable used to run cargo commands
CARGO_COMMAND = 'cargo'

#: list of environment keys to filter from a environment dictionary
CARGO_SANITIZE_ENV_KEYS = [
    # users should use `RELENG_CARGO=<path>` to override
    'CARGO',
    # releng-tool manages offline state through cli options
    'CARGO_NET_OFFLINE',
    # compiler flag should be managed internally
    # ignore build environment options that should be managed internally
    'CARGO_BUILD_DEP_INFO_BASEDIR',
    'CARGO_BUILD_INCREMENTAL',
    'CARGO_BUILD_JOBS',
    'CARGO_BUILD_RUSTDOCFLAGS',
    'CARGO_BUILD_RUSTFLAGS',
    'CARGO_BUILD_TARGET',
    'CARGO_BUILD_TARGET_DIR',
    'CARGO_ENCODED_RUSTFLAGS',
    'CARGO_INCREMENTAL',
    'CARGO_INSTALL_ROOT',
    'CARGO_MAKEFLAGS',
    'CARGO_MANIFEST_DIR',
    'CARGO_MANIFEST_LINKS',
    'CARGO_TARGET_DIR',
    'DEBUG',
    'NUM_JOBS',
    'OPT_LEVEL',
    'OUT_DIR',
    'PROFILE',
    'RUSTFLAGS',
    'TARGET',
]

#: dictionary of environment entries append to the environment dictionary
CARGO_EXTEND_ENV = {
    # use project-specific cargo cache
    'CARGO_HOME': '$CACHE_DIR/.cargo',
}

#: cargo host tool helper
CARGO = RelengTool(CARGO_COMMAND,
    env_sanitize=CARGO_SANITIZE_ENV_KEYS, env_include=CARGO_EXTEND_ENV)
