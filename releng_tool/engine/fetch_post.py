# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PackageType
from releng_tool.tool.cargo import CARGO
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import note


def stage(engine, pkg):  # noqa: ARG001
    """
    handles the fetching (post) stage for a package

    With a provided engine and package instance, the fetching (post) stage
    will be processed.

    Args:
        engine: the engine
        pkg: the package being fetched

    Returns:
        ``True`` if the fetching stage is completed; ``False`` otherwise
    """
    assert pkg.type
    name = pkg.name
    debug('process fetch (post) stage: ' + name)

    # for cargo projects, vendor fetch any dependencies
    if pkg.type == PackageType.CARGO:
        note('fetching (post; cargo) {}...', name)

        if not CARGO.exists():
            err('unable to post-fetch package; cargo is not installed')
            return False

        cargo_args = [
            'vendor',
            '$CACHE_DIR/.cargo-vendor',
            # provide an explicit cargo path (to prevent cargo from searching)
            '--manifest-path',
            'Cargo.toml',
            # this is a shared cargo vendor path
            '--no-delete',
            # version cached dependencies (to prevent conflicts)
            '--versioned-dirs',
        ]
        cargo_args.extend(pkg.cargo_depargs)

        if not CARGO.execute(cargo_args, cwd=pkg.build_dir):
            err('failed to vendor-fetch cargo project: {}', name)
            return False

    return True
