# -*- coding: utf-8 -*-
# Copyright 2018-2020 releng-tool

from __future__ import absolute_import
from .log import *
from enum import Enum
from io import open
import hashlib
import os

#: size of blocks read when calculating the hash for a file
HASH_READ_BLOCKSIZE = 1048576

class HashResult(Enum):
    """
    result of a hash verification check

    Attributes:
        UNKNOWN: unknown result
        BAD_FORMAT: a bad format was detected in hash file
        BAD_PATH: a path is missing or cannot be read
        EMPTY: the hash file is empty
        MISMATCH: detected a mismatch between provided and calculated hash
        MISSING_ARCHIVE: missing hash for archive
        MISSING_LISTED: a listed file is missing in sources
        UNSUPPORTED: an unsupported hash type was provided
        VERIFIED: hash verification has completed
    """
    UNKNOWN = 0
    BAD_FORMAT = 1
    BAD_PATH = 2
    EMPTY = 3
    MISMATCH = 4
    MISSING_ARCHIVE = 5
    MISSING_LISTED = 6
    UNSUPPORTED = 7
    VERIFIED = 8

class BadFileHashLoadError(Exception):
    """
    raised when a file could not be loaded for hash information
    """
    pass

class BadFormatHashLoadError(Exception):
    """
    raised when invalid format/contents is detected in a hash file
    """
    pass

def load(hash_file):
    """
    load hash entries from a provided file

    The UTF-8 encoded file ``hash_file`` will be loaded for defined hash
    entries. A hash entry is a 3-tuple defining the type of hash algorithm used,
    the hash value expected and the asset associated with the hash. A tuple
    entry is defined on a single line with each entry separated by whitespace
    characters.

    A file with no entries defined will return an empty list.

    Comments are permitted in the file. Lines leading with a ``#`` character or
    inlined leading ``#`` character after a whitespace character will be
    ignored.

    Args:
        hash_file: the file

    Returns:
        a list of hash entry tuples (if any exist)

    Raises:
        BadFileHashLoadError: the hash file cannot be found or loaded
        BadFormatHashLoadError: a format issue has been detected
    """
    try:
        with open(hash_file, mode='r', encoding='utf_8') as f:
            data = f.readlines()
    except IOError:
        raise BadFileHashLoadError()

    # strip and split into chunks
    data = [x.split() for x in data if x.strip()]

    for idx, entry in enumerate(data):
        # remove comments
        for idx2, parts in enumerate(entry):
            if parts.startswith('#'):
                del entry[idx2:]
                break
        if not entry:
            continue

        entry_len = len(entry)
        if entry_len > 3:
            raise BadFormatHashLoadError(
                'too many values for entry {}'.format(idx + 1))
        if entry_len < 3:
            raise BadFormatHashLoadError(
                'too few values for entry {}'.format(idx + 1))

    # compile a list of tuples with no empty entries
    return [tuple(x) for x in data if x]

def verify(hash_file, path, exclude=None, relaxed=False, quiet=False):
    """
    verify a file or directory with the hashes defined in the provided hash file

    Performs a hash verification check for one or more files at the provided
    path. The provided ``hash_file`` will contain a series of expected hash
    entries for one or more files. If the provided ``path`` is a file, the
    file's hash will be compared to a matching entry in the hash file. If the
    provided ``path` is a directory, each entry defined in the ``hash_file``
    will be checked and verified. The ``hash_file`` is a UTF-8 encoded file
    containing 3-tuple entries defining the type of hash algorithm used, the
    hash value expected and the asset associated with the hash (see
    ``load_hashes``). On the successful verification of all files, this method
    will return ``HashResult.VERIFIED``. Other warning/error states for
    verification will be return with a respective ``HashResult`` value.

    Args:
        hash_file: the file containing hash information
        path: the file or directory to verify
        exclude: assets to exclude from the verification check
        relaxed: relax logging to only warn on detected missing/mismatched
        quiet: disablement of error messages to standard out

    Returns:
        the hash result (``HashResult``)
    """
    is_file = False
    if os.path.isdir(path):
        pass
    elif os.path.isfile(path):
        is_file = True
    else:
        return HashResult.BAD_PATH

    # load hashes
    try:
        hash_info = load(hash_file)
    except BadFileHashLoadError:
        return HashResult.BAD_PATH
    except BadFormatHashLoadError as e:
        if not quiet:
            err('hash file is not properly formatted')
            err("""\
The hash file provided is incorrectly formatted. The hash file expects lines
with the hash type, hash and target file provided. For example:

    sha1 f572d396fae9206628714fb2ce00f72e94f2258f my-file

Please correct the following hash file:

    Hash File: {}
      Details: {}""".format(hash_file, e))
        return HashResult.BAD_FORMAT

    # no hash information
    if not hash_info:
        return HashResult.EMPTY

    # if this is a target file, filter out other hash entries
    if is_file:
        target = os.path.basename(path)
        path = os.path.abspath(os.path.join(path, os.pardir))
        hash_info = [x for x in hash_info if x[2] == target]
        if not hash_info:
            return HashResult.MISSING_ARCHIVE

    # filter out excluded assets (if any)
    if exclude:
        hash_info = [x for x in hash_info if x[2] not in exclude]
        if not hash_info:
            return HashResult.EMPTY

    hash_catalog = {}
    for type, hash, asset in hash_info:
        types = hash_catalog.setdefault(asset,{})
        types.setdefault(type,[]).append(hash.lower())

    for asset, type_hashes in hash_catalog.items():
        type_hashes.keys()
        hashers = {}
        for hash_type in type_hashes.keys():
            hashers[hash_type] = _getHasher(hash_type)
            if not hashers[hash_type]:
                if not quiet:
                    err('unsupported hash type')
                    err("""\
The hash file defines a hash type not supported by the releng-tool. Officially
supported hash types are FIPS-180 algorithms (sha1, sha224, sha256, sha384 and
sha512) as well as (but not recommended) RSA'S MD5 algorithm. Other algorithms,
while unofficially supported, can be used if provided by the system's OpenSSL
library.

     Hash File: {}
 Provided Type: {}""".format(hash_file, type))
                return HashResult.UNSUPPORTED

        target_file = os.path.join(path, asset)
        try:
            with open(target_file, 'rb') as f:
                buf = f.read(HASH_READ_BLOCKSIZE)
                while buf:
                    for hasher in hashers.values():
                        hasher.update(buf)
                    buf = f.read(HASH_READ_BLOCKSIZE)
        except IOError:
            if not quiet:
                if relaxed:
                    warn('missing expected file for verification: ' + asset)
                else:
                    err('missing expected file for verification')
                    err("""\
A defined hash entry cannot be verified since the target file does not exist.
Ensure the hash file correctly names an expected file.

    Hash File: {}
         File: {}""".format(hash_file, asset))
            return HashResult.MISSING_LISTED

        has_match = True
        for hash_type, hasher in hashers.items():
            debug('calculated-hash: {} {}:{}'.format(asset, hash_type, hash))
            digest = hasher.hexdigest()
            hashes = type_hashes[hash_type]
            if digest not in hashes:
                if not quiet:
                    if relaxed:
                        warn('hash mismatch detected: ' + asset)
                    else:
                        provided = ''
                        for hash in hashes:
                            provided += '\n     Provided: {}'.format(hash)

                        err("""hash mismatch detected\

    Hash File: {}
         File: {}
     Detected: {}{}""".format(hash_file, asset, digest, provided))
                return HashResult.MISMATCH

    return HashResult.VERIFIED

def _getHasher(type):
    """
    obtain a hasher instance from the provided type

    Finds and returns an instance which is capable of performing hashing
    operations of an algorithm defined by the ``type`` provided. In the event
    that a hasher cannot be found, this method will return ``None``.

    Args:
        type: the type of hash

    Returns:
        the hasher instance; ``None`` if the hash type is not supported
    """
    type = type.lower()
    func = getattr(hashlib, type, None)
    if func:
        return func()
    return None
