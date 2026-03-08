# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.log import verbose
import json
import os


def generate_json(sbom, cache):
    """
    generate a JSON format sbom file

    Compiles a JSON-formatted software build-of-materials document based
    on the cache information populated from a releng-tool project.

    Args:
        sbom: sbom manager instance
        cache: the sbom cache
    """

    verbose('writing sbom (json)')
    sbom_file = os.path.join(sbom.opts.out_dir, 'sbom.json')
    with open(sbom_file, 'w') as f:
        json.dump(cache, f, indent=4)

    sbom.generated.append(sbom_file)
