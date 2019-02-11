#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ..api import RelengFetchOptions
from ..defs import *
from ..fetch.bzr import fetch as fetchBzr
from ..fetch.cvs import fetch as fetchCvs
from ..fetch.git import fetch as fetchGit
from ..fetch.mercurial import fetch as fetchMercurial
from ..fetch.scp import fetch as fetchScp
from ..fetch.svn import fetch as fetchSvn
from ..fetch.url import fetch as fetchUrl
from ..util.api import replicatePackageAttribs
from ..util.hash import HashResult
from ..util.hash import verify as verify_hashes
from ..util.io import ensureDirectoryExists
from ..util.io import generateTempDir as tempDir
from ..util.io import interimWorkingDirectory
from ..util.io import pathRemove
from ..util.log import *
import os
import shutil
import sys

def stage(engine, pkg):
    """
    handles the fetching stage for a package

    With a provided engine and package instance, the fetching stage will be
    processed.

    Args:
        engine: the engine
        pkg: the package being fetched

    Returns:
        ``True`` if the fetching stage is completed; ``False`` otherwise
    """
    assert pkg.vcs_type
    name = pkg.name
    debug('process fetch stage: ' + name)

    # local sources mode requires internal sources to be already checked out
    if pkg.is_internal and engine.opts.local_srcs:
        if os.path.isdir(pkg.build_dir):
            return True

        err('missing local sources for internal package: ' + name)
        log("""\
The active configuration is flagged for 'local sources' mode; however, an
internal package cannot be found in the local system. Before continuing, ensure
you have checked out all internal packages on your local system (or, disable the
local sources option to use the default process).

       Package: {}
 Expected Path: {}""".format(name, pkg.build_dir))
        return False

    # if the vcs-type is archive-based, flag that hash checks are needed
    perform_file_hash_check = False
    if pkg.vcs_type == VcsType.URL:
        perform_file_hash_check = True

    fetch_opts = RelengFetchOptions()
    replicatePackageAttribs(fetch_opts, pkg)
    fetch_opts.cache_dir = pkg.cache_dir
    fetch_opts.ext = pkg.ext_modifiers
    fetch_opts.name = name
    fetch_opts.revision = pkg.revision
    fetch_opts.site = pkg.site
    fetch_opts.version = pkg.version

    cache_filename = os.path.basename(pkg.cache_file)
    out_dir = engine.opts.out_dir
    with tempDir(out_dir) as work_dir, tempDir(out_dir) as interim_cache_dir:
        with interimWorkingDirectory(work_dir):
            interim_cache_file = os.path.join(interim_cache_dir, cache_filename)
            fetch_opts.cache_file = interim_cache_file
            fetch_opts.work_dir = work_dir

            if os.path.exists(pkg.cache_file):
                if perform_file_hash_check:
                    hr = verify_hashes(
                        pkg.hash_file, pkg.cache_file, relaxed=True)

                    if hr == HashResult.VERIFIED:
                        return True
                    elif hr == HashResult.BAD_PATH:
                        if not pkg.is_internal:
                            warn('missing hash file for package: ' + name)
                        return True # no hash file to compare with; assuming ok
                    elif hr == HashResult.EMPTY:
                        if not pkg.is_internal:
                            warn('hash file for package is empty: ' + name)
                        return True # empty hash file; assuming ok
                    elif hr == HashResult.MISMATCH:
                        if not pathRemove(pkg.cache_file):
                            return False
                    elif hr in (HashResult.BAD_FORMAT, HashResult.UNSUPPORTED):
                        return False
                    elif hr == HashResult.MISSING_ARCHIVE:
                        err('missing archive hash for verification')
                        log("""\
The hash file for this package does not have an entry for the cache file to be
verified. Ensure the hash file defines an entry for the expected cache file:

    Hash File: {}
         File: {}""".format(pkg.hash_file, cache_filename))
                        return False
                    else:
                        err('invalid fetch operation (internal error; '
                            'hash-check failure: {})'.format(hr))
                        return False
                else:
                    return True

            # find fetching method for the target vcs-type
            fetcher = None
            if pkg.vcs_type in engine.registry.fetch_types:
                def _(opts):
                    return engine.registry.fetch_types[pkg.vcs_type].fetch(
                        pkg.vcs_type, opts)
                fetcher = _
            elif pkg.vcs_type == VcsType.BZR:
                fetcher = fetchBzr
            elif pkg.vcs_type == VcsType.CVS:
                fetcher = fetchCvs
            elif pkg.vcs_type == VcsType.GIT:
                fetcher = fetchGit
            elif pkg.vcs_type == VcsType.HG:
                fetcher = fetchMercurial
            elif pkg.vcs_type == VcsType.SCP:
                fetcher = fetchScp
            elif pkg.vcs_type == VcsType.SVN:
                fetcher = fetchSvn
            elif pkg.vcs_type == VcsType.URL:
                fetcher = fetchUrl

            if not fetcher:
                err('fetch type is not implemented: {}'.format(pkg.vcs_type))
                return False

            # if this is url-type location, attempt to search on the mirror
            # first (if configured)
            fetched = None
            if engine.opts.url_mirror and pkg.vcs_type == VcsType.URL:
                original_site = fetch_opts.site
                new_site = engine.opts.url_mirror + cache_filename
                if original_site != new_site:
                    fetch_opts.site = new_site
                    fetched = fetcher(fetch_opts)
                    fetch_opts.site = original_site

            # perform the fetch request (if not already fetched)
            if not fetched:
                fetched = fetcher(fetch_opts)
                if not fetched:
                    return False

            # if the fetch type has populated the package's cache directory
            # directly, we are done
            if fetched == pkg.cache_dir:
                pass
            # if the fetch type has returned a file, the file needs to be hash
            # checked and then be moved into the download cache
            elif fetched == interim_cache_file:
                if perform_file_hash_check:
                    hr = verify_hashes(pkg.hash_file, fetched)
                    if hr == HashResult.VERIFIED:
                        pass
                    elif hr == HashResult.BAD_PATH:
                        if not pkg.is_internal:
                            warn('missing hash file for package: ' + name)
                    elif hr == HashResult.EMPTY:
                        if not pkg.is_internal:
                            warn('hash file for package is empty: ' + name)
                    elif hr == HashResult.MISMATCH:
                        return False
                    elif hr in (HashResult.BAD_FORMAT, HashResult.UNSUPPORTED):
                        return False
                    elif hr == HashResult.MISSING_ARCHIVE:
                        err('missing archive hash for verification')
                        log("""\
The hash file for this package does not have an entry for the cache file to be
verified. Ensure the hash file defines an entry for the expected cache file:

    Hash File: {}
         File: {}""".format(pkg.hash_file, cache_filename))
                        return False
                    else:
                        err('invalid fetch operation (internal error; '
                            'hash-check failure: {})'.format(hr))
                        return False

                debug('fetch successful; moving cache file')

                # ensure the download directory exists
                if not ensureDirectoryExists(engine.opts.dl_dir):
                    return False

                try:
                    shutil.move(interim_cache_file, pkg.cache_file)
                except:
                    err('invalid fetch operation (internal error; fetch mode '
                        '"{}" has provided a missing cache file)'.format(
                            pkg.vcs_type))
                    return False
            else:
                err('invalid fetch operation (internal error; fetch mode "{}" '
                    'has returned an unsupported value)'.format(pkg.vcs_type))
                return False

    return True
