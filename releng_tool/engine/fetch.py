# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.api import RelengFetchOptions
from releng_tool.defs import VcsType
from releng_tool.fetch.bzr import fetch as fetch_bzr
from releng_tool.fetch.cvs import fetch as fetch_cvs
from releng_tool.fetch.git import fetch as fetch_git
from releng_tool.fetch.mercurial import fetch as fetch_mercurial
from releng_tool.fetch.scp import fetch as fetch_scp
from releng_tool.fetch.svn import fetch as fetch_svn
from releng_tool.fetch.url import fetch as fetch_url
from releng_tool.tool.gpg import GPG
from releng_tool.util.api import replicate_package_attribs
from releng_tool.util.hash import HashResult
from releng_tool.util.hash import verify as verify_hashes
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.io import generate_temp_dir
from releng_tool.util.io import interim_working_dir
from releng_tool.util.io import path_remove
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
import os
import shutil

def stage(engine, pkg, ignore_cache):
    """
    handles the fetching stage for a package

    With a provided engine and package instance, the fetching stage will be
    processed.

    Args:
        engine: the engine
        pkg: the package being fetched
        ignore_cache: always attempt to ignore the cache

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
    perform_file_asc_check = False
    perform_file_hash_check = False
    if pkg.vcs_type == VcsType.URL:
        perform_file_asc_check = os.path.exists(pkg.asc_file)
        perform_file_hash_check = True

    fetch_opts = RelengFetchOptions()
    replicate_package_attribs(fetch_opts, pkg)
    fetch_opts.cache_dir = pkg.cache_dir
    fetch_opts.ext = pkg.ext_modifiers
    fetch_opts.ignore_cache = ignore_cache
    fetch_opts.name = name
    fetch_opts.revision = pkg.revision
    fetch_opts.site = pkg.site
    fetch_opts.version = pkg.version
    fetch_opts._quirks = engine.opts.quirks

    cache_filename = os.path.basename(pkg.cache_file)
    out_dir = engine.opts.out_dir
    with generate_temp_dir(out_dir) as work_dir, \
            generate_temp_dir(out_dir) as interim_cache_dir:
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
            if engine.opts.devmode and pkg.devmode_ignore_cache is not None:
                fetch_opts.ignore_cache = pkg.devmode_ignore_cache

                if pkg.devmode_ignore_cache and os.path.exists(pkg.cache_file):
                    verbose('removing cache file (per configuration): ' + name)
                    if not path_remove(pkg.cache_file):
                        return False
            # force explicit ignore cache when not in development mode
            elif not engine.opts.devmode and ignore_cache is None:
                fetch_opts.ignore_cache = False

            if os.path.exists(pkg.cache_file):
                rv = None
                if perform_file_hash_check:
                    hr = verify_hashes(
                        pkg.hash_file, pkg.cache_file, relaxed=True)

                    if hr == HashResult.VERIFIED:
                        rv = True
                    elif hr == HashResult.BAD_PATH:
                        if not perform_file_asc_check and not pkg.is_internal:
                            warn('missing hash file for package: ' + name)
                        rv = True # no hash file to compare with; assuming ok
                    elif hr == HashResult.EMPTY:
                        if not pkg.is_internal:
                            warn('hash file for package is empty: ' + name)
                        rv = True # empty hash file; assuming ok
                    elif hr == HashResult.MISMATCH:
                        if not path_remove(pkg.cache_file):
                            rv = False
                    elif hr in (HashResult.BAD_FORMAT, HashResult.UNSUPPORTED):
                        rv = False
                    elif hr == HashResult.MISSING_ARCHIVE:
                        if not perform_file_asc_check:
                            err("""\
missing archive hash for verification

The hash file for this package does not have an entry for the cache file to be
verified. Ensure the hash file defines an entry for the expected cache file:

    Hash File: {}
         File: {}""".format(pkg.hash_file, cache_filename))
                            rv = False
                    else:
                        err('invalid fetch operation (internal error; '
                            'hash-check failure: {})'.format(hr))
                        rv = False
                else:
                    rv = True

                if rv is not False and perform_file_asc_check and \
                        os.path.exists(pkg.cache_file):
                    if GPG.validate(pkg.asc_file, pkg.cache_file):
                        rv = True
                    else:
                        if not path_remove(pkg.cache_file):
                            err("""\
failed to validate against ascii-armor

Validation of a package resource failed to verify against a provided ASCII-armor
file. Ensure that the package's public key has been registered into gpg.

 ASC File: {}
     File: {}""".format(pkg.asc_file, cache_filename))
                            rv = False
                        else:
                            rv = None

                if rv is not None:
                    if ignore_cache:
                        verbose('ignoring cache not supported for package: {}',
                            name)
                    return rv

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
                        if not perform_file_asc_check and not pkg.is_internal:
                            warn('missing hash file for package: ' + name)
                    elif hr == HashResult.EMPTY:
                        if not pkg.is_internal:
                            warn('hash file for package is empty: ' + name)
                    elif hr == HashResult.MISMATCH:
                        return False
                    elif hr in (HashResult.BAD_FORMAT, HashResult.UNSUPPORTED):
                        return False
                    elif hr == HashResult.MISSING_ARCHIVE:
                        if not perform_file_asc_check:
                            err("""\
missing archive hash for verification

The hash file for this package does not have an entry for the cache file to be
verified. Ensure the hash file defines an entry for the expected cache file:

    Hash File: {}
         File: {}""".format(pkg.hash_file, cache_filename))
                            return False
                    else:
                        err('invalid fetch operation (internal error; '
                            'hash-check failure: {})'.format(hr))
                        return False

                if perform_file_asc_check:
                    if not GPG.validate(pkg.asc_file, interim_cache_file):
                        err("""\
failed to validate against ascii-armor

Validation of a package resource failed to verify against a provided ASCII-armor
file. Ensure that the package's public key has been registered into gpg.

     ASC File: {}
         File: {}""".format(pkg.asc_file, cache_filename))
                        return False

                debug('fetch successful; moving cache file')

                # ensure the download directory exists
                if not ensure_dir_exists(engine.opts.dl_dir):
                    return False

                try:
                    shutil.move(interim_cache_file, pkg.cache_file)
                except shutil.Error:
                    err('invalid fetch operation (internal error; fetch mode '
                        '"{}" has provided a missing cache file)'.format(
                            pkg.vcs_type))
                    return False
            else:
                err('invalid fetch operation (internal error; fetch mode "{}" '
                    'has returned an unsupported value)'.format(pkg.vcs_type))
                return False

    return True
