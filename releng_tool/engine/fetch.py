# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.api import RelengFetchOptions
from releng_tool.defs import VcsType
from releng_tool.fetch.brz import fetch as fetch_brz
from releng_tool.fetch.bzr import fetch as fetch_bzr
from releng_tool.fetch.cvs import fetch as fetch_cvs
from releng_tool.fetch.file import fetch as fetch_file
from releng_tool.fetch.git import fetch as fetch_git
from releng_tool.fetch.mercurial import fetch as fetch_mercurial
from releng_tool.fetch.perforce import fetch as fetch_perforce
from releng_tool.fetch.rsync import fetch as fetch_rsync
from releng_tool.fetch.scp import fetch as fetch_scp
from releng_tool.fetch.svn import fetch as fetch_svn
from releng_tool.fetch.url import fetch as fetch_url
from releng_tool.tool.gpg import GPG
from releng_tool.util.api import replicate_package_attribs
from releng_tool.util.hash import HashResult
from releng_tool.util.hash import verify as verify_hashes
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_remove import path_remove
from releng_tool.util.io_temp_dir import temp_dir
from releng_tool.util.io_wd import wd
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
import os
import shutil


def stage(engine, pkg, ignore_cache, extra_opts):
    """
    handles the fetching stage for a package

    With a provided engine and package instance, the fetching stage will be
    processed.

    Args:
        engine: the engine
        pkg: the package being fetched
        ignore_cache: always attempt to ignore the cache
        extra_opts: extra options for the fetch operation (if applicable)

    Returns:
        ``True`` if the fetching stage is completed; ``False`` otherwise
    """
    assert pkg.vcs_type
    name = pkg.name
    debug('process fetch stage: ' + name)

    # packages flagged for local sources requires to be already checked out
    if pkg.local_srcs and os.path.isdir(pkg.build_dir):
        return True

    # if the vcs-type is archive-based, flag that hash checks are needed
    perform_file_asc_check = False
    perform_file_hash_check = False
    if pkg.vcs_type in (VcsType.FILE, VcsType.URL):
        perform_file_asc_check = os.path.exists(pkg.asc_file)
        perform_file_hash_check = True

    # find fetching method for the target vcs-type
    fetcher = None
    if pkg.vcs_type in engine.registry.fetch_types:
        def _(opts):
            return engine.registry.fetch_types[pkg.vcs_type].fetch(
                pkg.vcs_type, opts)
        fetcher = _
    elif pkg.vcs_type == VcsType.BRZ:
        fetcher = fetch_brz
    elif pkg.vcs_type == VcsType.BZR:
        fetcher = fetch_bzr
    elif pkg.vcs_type == VcsType.CVS:
        fetcher = fetch_cvs
    elif pkg.vcs_type == VcsType.FILE:
        fetcher = fetch_file
    elif pkg.vcs_type == VcsType.GIT:
        fetcher = fetch_git
    elif pkg.vcs_type == VcsType.HG:
        fetcher = fetch_mercurial
    elif pkg.vcs_type == VcsType.PERFORCE:
        fetcher = fetch_perforce
    elif pkg.vcs_type == VcsType.RSYNC:
        fetcher = fetch_rsync
    elif pkg.vcs_type == VcsType.SCP:
        fetcher = fetch_scp
    elif pkg.vcs_type == VcsType.SVN:
        fetcher = fetch_svn
    elif pkg.vcs_type == VcsType.URL:
        fetcher = fetch_url

    # if this package is a locally sources one and the fetcher type is not
    # supported, clear it
    if pkg.local_srcs:
        supported_local_fetchers = [
            VcsType.CVS,
            VcsType.GIT,
            VcsType.HG,
            VcsType.SVN,
        ]
        if pkg.vcs_type not in supported_local_fetchers:
            fetcher = None

    if not fetcher:
        if pkg.local_srcs:
            err('''\
missing local sources for internal package: {0}

The active configuration is flagged for 'local sources' mode; however, an
internal package cannot be found in the local system. Before continuing, ensure
you have checked out all internal packages on your local system (or, disable the
local sources option to use the default process).

       Package: {0}
 Expected Path: {1}''', name, pkg.build_dir)
        else:
            err('fetch type is not implemented: {}', pkg.vcs_type)

        return False

    # prepare fetch options
    fetch_opts = RelengFetchOptions()
    replicate_package_attribs(fetch_opts, pkg)
    fetch_opts.cache_dir = pkg.cache_dir
    fetch_opts.ext = pkg.ext_modifiers
    fetch_opts.extra_opts = extra_opts
    fetch_opts.ignore_cache = ignore_cache
    fetch_opts.name = name
    fetch_opts.revision = pkg.revision
    fetch_opts.site = pkg.site
    fetch_opts.version = pkg.version
    fetch_opts._mirror = False
    fetch_opts._quirks = engine.opts.quirks
    fetch_opts._urlopen_context = engine.opts.urlopen_context

    cache_filename = os.path.basename(pkg.cache_file)
    out_dir = engine.opts.out_dir
    with temp_dir(out_dir) as work_dir, temp_dir(out_dir) as interim_cache_dir:
        with wd(work_dir):
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

            # remove cache file if there is a force request to ignore the cache
            elif engine.opts.force and ignore_cache:
                if os.path.exists(pkg.cache_file):
                    verbose('removing cache file (forced): ' + name)
                    if not path_remove(pkg.cache_file):
                        return False

            # force explicit ignore cache (to off) when not in development mode
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
                        rv = True  # no hash file to compare with; assuming ok
                    elif hr == HashResult.EMPTY:
                        if not pkg.is_internal:
                            warn('hash file for package is empty: ' + name)
                        rv = True  # empty hash file; assuming ok
                    elif hr == HashResult.MISMATCH:
                        if not path_remove(pkg.cache_file):
                            rv = False
                    elif hr in (HashResult.BAD_FORMAT, HashResult.UNSUPPORTED):
                        rv = False
                    elif hr == HashResult.MISSING_ARCHIVE:
                        if not perform_file_asc_check:
                            err('''\
missing archive hash for verification

The hash file for this package does not have an entry for the cache file to be
verified. Ensure the hash file defines an entry for the expected cache file:

    Hash File: {}
         File: {}''', pkg.hash_file, cache_filename)
                            rv = False
                    else:
                        err('invalid fetch operation (internal error; '
                            'hash-check failure: {})', hr)
                        rv = False
                else:
                    rv = True

                if rv is not False and perform_file_asc_check and \
                        os.path.exists(pkg.cache_file):
                    if GPG.validate(pkg.asc_file, pkg.cache_file):
                        rv = True
                    elif not path_remove(pkg.cache_file):
                        err('''\
failed to validate against ascii-armor

Validation of a package resource failed to verify against a provided ASCII-armor
file. Ensure that the package's public key has been registered into gpg.

 ASC File: {}
     File: {}''', pkg.asc_file, cache_filename)
                        rv = False
                    else:
                        rv = None

                if rv is not None:
                    if ignore_cache:
                        verbose('ignoring cache not supported for package: {}',
                            name)
                    return rv

            # if this is url-type location, attempt to search on the mirror
            # first (if configured)
            fetched = None
            if engine.opts.url_mirror and pkg.vcs_type == VcsType.URL:
                original_site = fetch_opts.site
                url_mirror = engine.opts.url_mirror.format(
                    name=pkg.name,
                    version=pkg.version,
                )
                new_site = url_mirror + cache_filename
                if original_site != new_site:
                    fetch_opts.site = new_site

                    # we have configured for a new url mirror and are about
                    # to fetch; but if this is an external project and we
                    # should only be fetching from the mirror, continue the
                    # fetch operation as normal since we will only attempt a
                    # single fetch event
                    if pkg.is_internal or not engine.opts.only_mirror:
                        fetch_opts._mirror = True
                        fetched = fetcher(fetch_opts)
                        fetch_opts._mirror = False

                        fetch_opts.site = original_site
                    else:
                        verbose('only mirror fetch for package: {}', name)

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
                            err('''\
missing archive hash for verification

The hash file for this package does not have an entry for the cache file to be
verified. Ensure the hash file defines an entry for the expected cache file:

    Hash File: {}
         File: {}''', pkg.hash_file, cache_filename)
                            return False
                    else:
                        err('invalid fetch operation (internal error; '
                            'hash-check failure: {})', hr)
                        return False

                if perform_file_asc_check:
                    if not GPG.validate(pkg.asc_file, interim_cache_file):
                        err('''\
failed to validate against ascii-armor

Validation of a package resource failed to verify against a provided ASCII-armor
file. Ensure that the package's public key has been registered into gpg.

     ASC File: {}
         File: {}''', pkg.asc_file, cache_filename)
                        return False

                debug('fetch successful; moving cache file')

                # ensure the cache container/directory exists
                cache_dir = os.path.dirname(pkg.cache_file)
                if not mkdir(cache_dir):
                    return False

                try:
                    shutil.move(interim_cache_file, pkg.cache_file)
                except shutil.Error:
                    err('invalid fetch operation (internal error; fetch mode '
                        '"{}" has provided a missing cache file)', pkg.vcs_type)
                    return False
            else:
                err('invalid fetch operation (internal error; fetch mode "{}" '
                    'has returned an unsupported value)', pkg.vcs_type)
                return False

    return True
