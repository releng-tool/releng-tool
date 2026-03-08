# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

# map of python hashlib names to CycloneDX-compatible algorithm names
COMPAT_CYCLONEDX_HASH_ID = {
    'blake2b': 'BLAKE2b-512',
    'md5': 'MD5',
    'sha1': 'SHA-1',
    'sha256': 'SHA-256',
    'sha384': 'SHA-384',
    'sha3_256': 'SHA3-256',
    'sha3_384': 'SHA3-384',
    'sha3_512': 'SHA3-512',
    'sha512': 'SHA-512',
}
