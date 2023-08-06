from __future__ import print_function

import re
import json
import os
import tempfile
import logging
import random
import time
import pkg_resources
import socket

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


class InvalidAPIKeyError(Exception):
    """when the api key is wrong"""


class SubmitError(Exception):
    """when we can't submit the result"""


class BadRequestError(Exception):
    """when we can't submit the result"""


try:
    timeout_exception = requests.exceptions.ReadTimeout
except AttributeError:
    timeout_exception = requests.exceptions.Timeout


ops_exceptions = (
    requests.exceptions.ConnectionError,
    timeout_exception,
)


_UAS = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',

    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 '
    'Firefox/62.0',

    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 '
    '(KHTML, like Gecko) Version/9.1.4 Safari/601.8.7',

    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/53.0.2743.117 Safari/537.36',

    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.2) Gecko/20100101 '
    'Firefox/49.3',

    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.2) Gecko/20100101 '
    'Firefox/51.3',

    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
    'like Gecko) Chrome/63.0.3239.132 Safari/537.36',

    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:57.0) Gecko/20100101 '
    'Firefox/58.0',

    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',

    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
    'like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14394',

)


def requests_retry_session(
    retries=7,
    backoff_factor=0.4,
    status_forcelist=(500, 502, 504),
    session=None,
):
    """Opinionated wrapper that creates a requests session with a
    HTTPAdapter that sets up a Retry policy that includes connection
    retries.

    If you do the more naive retry by simply setting a number. E.g.::

        adapter = HTTPAdapter(max_retries=3)

    then it will raise immediately on any connection errors.
    Retrying on connection errors guards better on unpredictable networks.
    From http://docs.python-requests.org/en/master/api/?highlight=retries#requests.adapters.HTTPAdapter
    it says: "By default, Requests does not retry failed connections."

    The backoff_factor is documented here:
    https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.retry.Retry
    A default of retries=3 and backoff_factor=0.3 means it will sleep like::

        [0.3, 0.6, 1.2]
    """  # noqa
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


realistic_session = requests_retry_session()


def realistic_request(url, verify=True, timeout=.4):
    headers = {
        'Accept': (
            'text/html,application/xhtml+xml,application/xml,text/xml'
            ';q=0.9,*/*;q=0.8'
        ),
        'User-Agent': random.choice(_UAS),
        'Accept-Language': 'en-US,en;q=0.5',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    return realistic_session.get(
        url,
        headers=headers,
        verify=verify,
        timeout=timeout,
    )


class Runner:

    def __init__(
        self,
        api_key,
        domain,
        use_http=False,
        gently=False,
        logger=None,
        timeout=10,
        hostname=None,
    ):
        self.api_key = api_key
        self.domain = domain
        self.use_http = use_http
        self.gently = gently
        self.logger = logger or logging.getLogger(__name__)
        self.successes = 0
        self.failures = 0
        self.trimmings = 0
        self.timeout = int(timeout)
        if not hostname:
            try:
                hostname = socket.gethostname()
            except Exception:
                # No idea what kind of errors this might be but best
                # be cautions since it's not super important.
                pass
        self.hostname = hostname

    def get_url(self, path):
        url = self.use_http and 'http://' or 'https://'
        url += self.domain
        url += path
        return url

    def log(self, *args, **kwargs):
        self.logger.info(' '.join(str(x) for x in args), **kwargs)

    def repeat(self):
        session = requests_retry_session(backoff_factor=0.2)
        while True:
            try:
                fetch_url = self.get_url('/api/downloader/next/')
                self.log('Fetching next URL from ', fetch_url)

                next_url_response = session.get(fetch_url, headers={
                    'API-Key': self.api_key
                }, timeout=self.timeout)
                if next_url_response.status_code == 403:
                    raise InvalidAPIKeyError(self.api_key)
                elif next_url_response.status_code == 429:
                    self.log("Taking a biiig pause till there's more to do")
                    time.sleep(60 * 10)
                    continue
                elif next_url_response.status_code >= 500:
                    self.log(
                        "Fetching the next URL simply failed. "
                        "Trying again a little later."
                    )
                    time.sleep(60)
                    continue

                next_url = next_url_response.json()['url']
                self.log('Next URL to download:', next_url)

                submit_url = self.get_url('/api/downloader/submit/')

                if self.gently:
                    # min 8 second, max 8+5 seconds
                    sleep_time = 8 + random.random() * 5
                else:
                    # min 4 second, max 4+4 seconds
                    sleep_time = 4 + random.random() * 3

                response = realistic_request(next_url, timeout=self.timeout)
                if response.status_code == 404:
                    submit_response = requests.post(
                        submit_url,
                        data={
                            'notfound': True,
                            'url': next_url,
                        },
                        headers={
                            'API-Key': self.api_key
                        },
                        timeout=self.timeout
                    )
                    self.log('Reported URL not found {} (hostname: {})'.format(
                        next_url,
                        self.hostname,
                    ))
                    self.log('Sleeping for', round(sleep_time, 2), 'seconds')
                    time.sleep(sleep_time)
                    continue
                elif response.status_code != 200:
                    self.log(
                        'Failed to download', next_url,
                        'Status code:', response.status_code
                    )
                    time.sleep(30)
                    continue
                try:
                    html = json.dumps(response.json())
                except JSONDecodeError:
                    html = response.text

                self.log('Downloaded {} bytes (hostname: {})'.format(
                    format(len(html), ','),
                    self.hostname,
                ))

                if len(html) >= 1024 * 1024:
                    # If it's bigger than 1MB it's most likely too large
                    # to be realistic.
                    self.log(
                        'Skipping {} because the HTML is far too large '
                        '({} bytes)'.format(
                            next_url,
                            format(len(html), ','),
                        )
                    )
                    submit_response = requests.post(
                        submit_url,
                        data={
                            'notfound': True,
                            'url': next_url,
                        },
                        headers={
                            'API-Key': self.api_key
                        },
                        timeout=self.timeout
                    )
                    self.log('Reported URL too large {}'.format(
                        next_url,
                    ))
                    continue

                size_before = len(html)
                html = trim_fat_html(html)
                size_after = len(html)

                print(
                    'Saved',
                    format(size_before - size_after, ','),
                    'bytes by trimming the html first.',
                    next_url,
                )

                payload = {
                    'url': next_url,
                    'html': html,
                    'hostname': self.hostname,
                    'trimmed': False,
                }
                if size_after < size_before:
                    payload['trimmed'] = True
                    self.trimmings += size_before - size_after

                submit_response = session.post(
                    submit_url,
                    data=payload,
                    headers={
                        'API-Key': self.api_key
                    },
                    timeout=self.timeout
                )

                if submit_response.status_code == 403:
                    raise InvalidAPIKeyError(self.api_key)
                elif submit_response.status_code == 400:
                    self.log(
                        'RESPONSE:',
                        response.content[:1000] + b'...' + response.content[-1000:]
                    )
                    self.log('PAYLOAD URL:', payload['url'])
                    self.log('PAYLOAD.html LENGTH:', len(payload['html']))
                    raise BadRequestError(response.content[:100])
                elif (
                    submit_response.status_code > 400 and
                    submit_response.status_code < 500
                ):
                    raise SubmitError(submit_response.status_code)

                self.successes += 1

                self.log(
                    'Response after submitting:',
                    str(next_url_response.json())
                )

                self.log('Sleeping for', round(sleep_time, 2), 'seconds')
                time.sleep(sleep_time)

                self.log('\n')

            except ops_exceptions as exc:
                self.failures += 1
                self.log(
                    'Operational error, sleeping for a bit',
                    exc_info=True
                )
                time.sleep(self.gently and 90 or 30)


def trim_fat_html(html):
    html = re.sub(
        r'<(script|preload|style|noscript|svg).*?</\1>(?s)',
        '',
        html,
        flags=re.I
    )
    meta_tag_names = re.compile(
        r'name="(description|keywords|theme-color|robots|viewport)"'
    )
    for each, tag in re.findall(r'(<(meta|link) .*?>)', html):
        if tag == 'meta':
            if (
                'itemprop="page_data"' in each or
                meta_tag_names.findall(each)
            ):
                html = html.replace(each, '')
        else:
            html = html.replace(each, '')
    return html


def run(*args, **kwargs):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if not kwargs.pop('foreground', None):
        log_filename = os.path.join(
            tempfile.gettempdir(),
            'songsearch-agent.log'
        )
        print('Logging to {}'.format(log_filename))
        logger.addHandler(logging.FileHandler(log_filename))
    verbose = kwargs.pop('verbose')
    if verbose:
        logger.addHandler(logging.StreamHandler())
    kwargs['logger'] = logger
    runner = Runner(*args, **kwargs)
    try:
        runner.repeat()
    except Exception:
        logger.error('Errored on repeat', exc_info=True)
        raise
    except KeyboardInterrupt:
        logger.info(
            '\nFinally....\n\t'
            'Successes={}\n\t'
            'Failures={}\n\t'
            'Trimmings={}\n'.format(
                runner.successes,
                runner.failures,
                format_size(runner.trimmings),
            )
        )
        raise


def format_size(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return '%3.1f%s%s' % (num, unit, suffix)
        num /= 1024.0
    return '%.1f%s%s' % (num, 'Yi', suffix)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'api_key',
        help="package (e.g. some-package==1.2.3 or just some-package)",
        nargs='?'
    )
    parser.add_argument(
        "-v, --verbose",
        help="Verbose output",
        action="store_true",
        dest='verbose',
    )
    parser.add_argument(
        "-f, --foreground",
        help="Log to stdout",
        action="store_true",
        dest='foreground',
    )
    parser.add_argument(
        "-V, --version",
        help="What version this is",
        action="store_true",
        dest='version',
    )
    parser.add_argument(
        "-g, --gently",
        help='Longer delay between each loop',
        action="store_true",
        dest='gently',
    )
    parser.add_argument(
        '-d, --domain',
        help='Domain name to send to',
        action='store',
        default='songsear.ch',
        dest='domain',
    )
    parser.add_argument(
        "--http",
        help="Use http instead of https",
        action="store_true",
    )
    args = parser.parse_args()
    if args.version:
        print(pkg_resources.get_distribution('songsearch-agent').version)
        return 0
    else:
        return run(
            args.api_key,
            domain=args.domain,
            use_http=args.http,
            gently=args.gently,
            verbose=args.verbose,
            foreground=args.foreground,
        )


if __name__ == '__main__':
    import sys
    sys.exit(main())
