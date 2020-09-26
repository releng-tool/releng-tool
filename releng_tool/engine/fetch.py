# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ..api import RelengFetchOptions
from ..defs import *
from ..fetch.bzr import fetch as fetch_bzr
from ..fetch.cvs import fetch as fetch_cvs
from ..fetch.git import fetch as fetch_git
from ..fetch.mercurial import fetch as fetch_mercurial
from ..fetch.scp import fetch as fetch_scp
from ..fetch.svn import fetch as fetch_svn
from ..fetch.url import fetch as fetch_url
from ..util.api import replicate_package_attribs
from ..util.hash import HashResult
from ..util.hash import verify as verify_hashes
from ..util.io import ensure_dir_exists
from ..util.io import generate_temp_dir
from ..util.io import interim_working_dir
from ..util.io import path_remove
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
        err("""\
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
    replicate_package_attribs(fetch_opts, pkg)
    fetch_opts.cache_dir = pkg.cache_dir
    fetch_opts.ext = pkg.ext_modifiers
    fetch_opts.name = name
    fetch_opts.revision = pkg.revision
    fetch_opts.site = pkg.site
    fetch_opts.version = pkg.version
    fetch_opts._quirks = engine.opts.quirks

    cache_filename = os.path.basename(pkg.cache_file)
    out_dir = engine.opts.out_dir
    with generate_temp_dir(out_dir) as work_dir, generate_temp_dir(out_dir) as interim_cache_dir:
        with interim_working_dir(work_dir):
            interim_cache_file = os.path.join(interim_cache_dir, cache_filename)
            fetch_opts.cache_file = interim_cache_file
            fetch_opts.work_dir = work_dir

            # check if file caching should be ignored
            #
            # In special cases, a developer may configure a project to have a
            # fetched source not to cache. For example, pulling from a branch of
            # a VCS source will make a cache file from the branch and will
            # remain until manually removed from a cache file. A user may wish
            # to re-build the local cache file after cleaning their project.
            # While the releng-tool framework separates fetching/extraction into
            # two parts, ignoring cached assets can be partially achieved by
            # just removing any detected cache file if a project is configured
            # to ignore a cache file.
            if engine.opts.devmode and pkg.devmode_ignore_cache:
                fetch_opts.ignore_cache = True

                if os.path.exists(pkg.cache_file):
                    verbose('removing cache file (per configuration): ' + name)
                    if not path_remove(pkg.cache_file):
                        return False

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
                        if not path_remove(pkg.cache_file):
                            return False
                    elif hr in (HashResult.BAD_FORMAT, HashResult.UNSUPPORTED):
                        return False
                    elif hr == HashResult.MISSING_ARCHIVE:
                        err('missing archive hash for verification')
                        err("""\
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
                fetcher = fetch_bzr
            elif pkg.vcs_type == VcsType.CVS:
                fetcher = fetch_cvs
            elif pkg.vcs_type == VcsType.GIT:
                fetcher = fetch_git
            elif pkg.vcs_type == VcsType.HG:
                fetcher = fetch_mercurial
            elif pkg.vcs_type == VcsType.SCP:
                fetcher = fetch_scp
            elif pkg.vcs_type == VcsType.SVN:
                fetcher = fetch_svn
            elif pkg.vcs_type == VcsType.URL:
                fetcher = fetch_url

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
                        err("""\
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
                if not ensure_dir_exists(engine.opts.dl_dir):
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
