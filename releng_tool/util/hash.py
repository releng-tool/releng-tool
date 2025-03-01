# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import warn
from releng_tool.util.strccenum import StrCcEnum
import hashlib
import os

#: size of blocks read when calculating the hash for a file
HASH_READ_BLOCKSIZE = 1048576

#: number of expected parts for a hash entry
HASH_ENTRY_PARTS = 3


class HashResult(StrCcEnum):
    """
    result of a hash verification check

    Attributes:
        BAD_FORMAT: a bad format was detected in hash file
        BAD_PATH: a path is missing or cannot be read
        EMPTY: the hash file is empty
        MISMATCH: detected a mismatch between provided and calculated hash
        MISSING_ARCHIVE: missing hash for archive
        MISSING_LISTED: a listed file is missing in sources
        UNSUPPORTED: an unsupported hash type was provided
        VERIFIED: hash verification has completed
    """
    BAD_FORMAT = 'bad_format'
    BAD_PATH = 'bad_path'
    EMPTY = 'empty'
    MISMATCH = 'mismatch'
    MISSING_ARCHIVE = 'missing_archive'
    MISSING_LISTED = 'missing_listed'
    UNSUPPORTED = 'unsupported'
    VERIFIED = 'verified'


class BadFileHashLoadError(Exception):
    """
    raised when a file could not be loaded for hash information
    """


class BadFormatHashLoadError(Exception):
    """
    raised when invalid format/contents is detected in a hash file
    """


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
        with open(hash_file, encoding='utf_8') as f:
            data = f.readlines()
    except OSError as ex:
        raise BadFileHashLoadError from ex

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
        if entry_len > HASH_ENTRY_PARTS:
            raise BadFormatHashLoadError(
                'too many values for entry {}'.format(idx + 1))
        if entry_len < HASH_ENTRY_PARTS:
            raise BadFormatHashLoadError(
                'too few values for entry {}'.format(idx + 1))

        # a hash entry may also include an associated key length (e.g. SHAKE);
        # if a key length is provided, ensure it is sane value
        if ':' in entry[0]:
            hash_type, _, hash_len = entry[0].partition(':')
            if hash_len:
                try:
                    if int(hash_len) <= 0:
                        raise BadFormatHashLoadError(
                            f'invalid has keylen for entry {idx + 1}')
                except ValueError as ex:
                    raise BadFormatHashLoadError(
                        f'invalid has keylen type for entry {idx + 1}') from ex

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
            err('''\
hash file is not properly formatted

The hash file provided is incorrectly formatted. The hash file expects lines
with the hash type, hash and target file provided. For example:

    sha1 f572d396fae9206628714fb2ce00f72e94f2258f my-file

Please correct the following hash file:

    Hash File: {}
      Details: {}''', hash_file, e)

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
    for type_, hash_, asset in hash_info:
        types = hash_catalog.setdefault(asset, {})
        types.setdefault(type_, []).append(hash_.lower())

    for asset, type_hashes in hash_catalog.items():
        hashers = {}
        for hash_entry in type_hashes:
            # extract the specific hash type, if the entry includes a key length
            hash_type, _, _ = hash_entry.partition(':')

            hashers[hash_entry] = _get_hasher(hash_type)
            if not hashers[hash_entry]:
                if not quiet:
                    err('''\
unsupported hash type

The hash file defines a hash type not supported by the releng-tool. Officially
supported hash types are FIPS supported algorithms provided by the Python
interpreter (e.g. sha1, sha224, sha256, sha384, sha512). Other algorithms,
while unofficially supported, can be used if provided by the system's OpenSSL
library.

     Hash File: {}
 Provided Type: {}''', hash_file, hash_type)

                debug('unsupported hash type: {}', hash_type)
                return HashResult.UNSUPPORTED

        target_file = os.path.join(path, asset)
        try:
            with open(target_file, 'rb') as f:
                buf = f.read(HASH_READ_BLOCKSIZE)
                while buf:
                    for hasher in hashers.values():
                        hasher.update(buf)
                    buf = f.read(HASH_READ_BLOCKSIZE)
        except OSError:
            if not quiet:
                if relaxed:
                    warn('missing expected file for verification: ' + asset)
                else:
                    err('''\
missing expected file for verification

A defined hash entry cannot be verified since the target file does not exist.
Ensure the hash file correctly names an expected file.

    Hash File: {}
         File: {}''', hash_file, asset)

            return HashResult.MISSING_LISTED

        for hash_entry, hasher in hashers.items():
            _, _, hash_len = hash_entry.partition(':')
            if hash_len:
                digest = hasher.hexdigest(int(hash_len))
            else:
                digest = hasher.hexdigest()

            debug('calculated-hash: {} {}:{}', asset, hash_entry, digest)
            hashes = type_hashes[hash_entry]
            if digest not in hashes:
                if not quiet:
                    if relaxed:
                        warn('hash mismatch detected: ' + asset)
                    else:
                        provided = ''
                        for hash_ in hashes:
                            provided += f'\n     Provided: {hash_}'

                        err('''\
hash mismatch detected

    Hash File: {}
         File: {}
     Detected: {}{}''', hash_file, asset, digest, provided)

                return HashResult.MISMATCH

    return HashResult.VERIFIED


def _get_hasher(hash_type):
    """
    obtain a hasher instance from the provided type

    Finds and returns an instance which is capable of performing hashing
    operations of an algorithm defined by the ``type`` provided. In the event
    that a hasher cannot be found, this method will return ``None``.

    Args:
        hash_type: the type of hash

    Returns:
        the hasher instance; ``None`` if the hash type is not supported
    """

    hash_type = hash_type.lower()
    func = getattr(hashlib, hash_type, None)
    if func:
        return func()
    return None
