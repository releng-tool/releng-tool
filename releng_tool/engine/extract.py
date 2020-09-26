# -*- coding: utf-8 -*-
# Copyright 2018-2020 releng-tool

from ..api import RelengExtractOptions
from ..defs import *
from ..extract.archive import extract as extract_archive
from ..extract.git import extract as extract_git
from ..extract.mercurial import extract as extract_mercurial
from ..util.api import replicate_package_attribs
from ..util.hash import HashResult
from ..util.hash import verify as verify_hashes
from ..util.io import interim_working_dir
from ..util.io import generate_temp_dir
from ..util.io import path_remove
from ..util.log import *
import os
import shutil
import sys

def stage(engine, pkg):
    """
    handles the extraction stage for a package

    With a provided engine and package instance, the extraction stage will be
    processed.

    Args:
        engine: the engine
        pkg: the package being extracted

    Returns:
        ``True`` if the extraction stage is completed; ``False`` otherwise
    """

    # internal packages in local sources mode do not have an extraction stage
    if pkg.is_internal and engine.opts.local_srcs:
        return True

    # skip packages flagged not to extract
    if pkg.no_extraction:
        return True

    note('extracting {}...'.format(pkg.name))
    sys.stdout.flush()

    extract_opts = RelengExtractOptions()
    replicate_package_attribs(extract_opts, pkg)
    extract_opts.cache_dir = pkg.cache_dir
    extract_opts.cache_file = pkg.cache_file
    extract_opts.ext = pkg.ext_modifiers
    extract_opts.name = pkg.name
    extract_opts.revision = pkg.revision
    extract_opts.strip_count = pkg.strip_count
    extract_opts.version = pkg.version
    extract_opts._extract_override = engine.opts.extract_override
    extract_opts._quirks = engine.opts.quirks

    if os.path.exists(pkg.build_dir):
        warn('build directory exists before extraction; removing')

        if not path_remove(pkg.build_dir):
            err('unable to cleanup build directory: ' + pkg.build_dir)
            return False

    # prepare and step into the a newly created working directory
    #
    # An extractor will take the contents of an archive, cache directory or
    # other fetched content and populate the "work" directory. On successful
    # extraction (or moving resources), the work directory will be moved to the
    # package's respective build directory.
    out_dir = engine.opts.out_dir
    with generate_temp_dir(out_dir) as work_dir:
        with interim_working_dir(work_dir):
            extract_opts.work_dir = work_dir

            extracter = None
            hash_exclude = []
            extract_types = engine.registry.extract_types
            if pkg.extract_type and pkg.extract_type in extract_types:
                def _(opts):
                    return engine.registry.extract_types[pkg.vcs_type].extract(
                        pkg.vcs_type, opts)
                extracter = _
            elif pkg.vcs_type in extract_types:
                extracter = extract_types[pkg.vcs_type].extract
            elif pkg.vcs_type == VcsType.GIT:
                extracter = extract_git
            elif pkg.vcs_type == VcsType.HG:
                extracter = extract_mercurial
            elif os.path.isfile(pkg.cache_file):
                cache_basename = os.path.basename(pkg.cache_file)
                hash_exclude.append(cache_basename)
                extracter = extract_archive

            if not extracter:
                err('extract type is not implemented: {}'.format(pkg.vcs_type))
                return False

            # perform the extract request
            extracted = extracter(extract_opts)
            if not extracted:
                return False

            result = verify_hashes(pkg.hash_file, work_dir, hash_exclude)
            if result == HashResult.VERIFIED:
                pass
            elif result == HashResult.BAD_PATH:
                if not pkg.is_internal:
                    warn('missing hash file for package: ' + pkg.name)
            elif result == HashResult.EMPTY:
                if not pkg.is_internal:
                    warn('hash file for package is empty: ' + pkg.name)
            elif result in (HashResult.BAD_FORMAT, HashResult.MISMATCH,
                    HashResult.MISSING_LISTED, HashResult.UNSUPPORTED):
                return False
            else:
                err('invalid extract operation (internal error; '
                    'hash-check failure: {})'.format(result))
                return False

        debug('extraction successful; moving sources into package output '
            'directory: ' + pkg.build_dir)
        shutil.move(work_dir, pkg.build_dir)

    return True
