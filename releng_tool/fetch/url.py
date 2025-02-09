# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.log import warn
from urllib.error import HTTPError
from urllib.request import urlopen
import math
import os
import random
import time

#: size of blocks read when downloading a resource
REQUEST_READ_BLOCKSIZE = 8192

#: total number of retries (including initial request) before giving up
RETRY_ATTEMPTS = 3

# the maximum duration (in seconds) to wait for a retry event
RETRY_DURATION = 10


def fetch(opts):
    """
    support fetching from url sources

    With provided fetch options (``RelengFetchOptions``), the fetch stage will
    be processed.

    Args:
        opts: fetch options

    Returns:
        the fetched cache file; ``None`` if fetching has failed
    """

    assert opts
    is_mirror = opts._mirror
    name = opts.name
    site = opts.site

    note('fetching {}...', name)

    attempt = 1
    while True:
        cache_file, code, msg = _fetch_attempt(opts)
        if cache_file:
            return cache_file

        # if too many attempts, stop
        if attempt > RETRY_ATTEMPTS:
            break

        # ignore non-transient errors
        if code not in [408, 429, 500, 502, 503, 504]:
            break

        # we still attempt a retry; first inform the user of the state
        warn('failed to download resource: {}\n'
            '    {}', site, msg)

        # configure the delay + jitter
        delay = RETRY_DURATION
        delay += random.uniform(0.0, 0.5)  # noqa: S311

        # wait the calculated delay before retrying again
        reported_delay = math.ceil(delay)
        log(f'retrying in {reported_delay} seconds...')
        time.sleep(delay)
        attempt += 1

    log_func = warn if is_mirror else err
    log_func('failed to download resource: {}\n'
        '    {}', site, msg)
    return None


def _fetch_attempt(opts):
    cache_file = opts.cache_file
    site = opts.site
    urlopen_context = opts._urlopen_context

    filename = os.path.basename(cache_file)

    read = 0
    log('requesting: ' + site)
    try:
        with urlopen(site, context=urlopen_context) as rsp:
            total = 0
            total_str = ''
            if 'content-length' in rsp.headers:
                try:
                    total = int(rsp.headers['content-length'])
                    total_str = display_size(total)
                except ValueError:
                    pass

            with open(cache_file, 'wb') as f:
                while True:
                    buf = rsp.read(REQUEST_READ_BLOCKSIZE)
                    if not buf:
                        break
                    read += len(buf)
                    read_str = display_size(read)

                    if total != read:
                        if total > 0:
                            pct = 100 * float(read) / float(total)
                            print('[{:02.0f}%] {}: {} of {}            '.format(
                                pct, filename, read_str, total_str), end='\r')
                        else:
                            print(' {}: {}            '.format(
                                filename, read_str), end='\r')

                    f.write(buf)
    except HTTPError as e:
        return None, e.code, e
    except Exception as e:
        return None, None, e
    finally:
        # cleanup any download progress prints
        if read > 0:
            log('')

    log('completed download ({})', display_size(read))
    return cache_file, None, None

def display_size(val):
    """
    return a human-readable count value for the provided byte count

    Accepts a byte count value and returns a string with a count value and
    binary prefix which describes the respective size.

    Args:
        val: the value (in bytes) to interpret

    Returns:
        the human-readable size
    """

    SZ = 1024.
    for unit in ['B', 'KiB', 'MiB', 'GiB']:
        if abs(val) < SZ:
            return '{:3.1f} {}'.format(val, unit)
        val /= SZ

    return '{:.1f} TiB'.format(val)
