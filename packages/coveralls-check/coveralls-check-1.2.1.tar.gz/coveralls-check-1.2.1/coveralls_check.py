from __future__ import print_function

import logging
from argparse import ArgumentParser

import backoff
import requests
import sys

POLL_URL = 'https://coveralls.io/builds/{}.json'
DONE_URL = 'https://coveralls.io/webhook'


def setup_logging():
    logger = logging.getLogger('backoff')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)


def message(args, covered, template):
    print(template.format(
        args.commit, covered, args.fail_under
    ))


def get_coverage(commit):
    response = requests.get(POLL_URL.format(commit))
    data = response.json()
    return data['covered_percent']


def decorate(func, args):
    interval = 10
    return backoff.on_predicate(
        backoff.constant,
        interval=interval, max_tries=args.max_wait*60/interval,
        jitter=lambda value: value,
    )(func)


def ensure_parallel_done(args):
    if args.parallel_build_number:
        response = requests.post(
            DONE_URL,
            params={'repo_token': args.repo_token},
            json={
                "payload": {
                    "build_num": args.parallel_build_number,
                    "status": "done"
                }
            }
        )
        if response.status_code == 200:
            print('Confirmed end of parallel build')
        else:
            print(
                'Attempt to confirmed end of parallel build got {}:\n{}'.format(
                    response.status_code, response.content
                )
            )
            sys.exit(1)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('commit', help='the commit hash to check')
    parser.add_argument('--fail-under', type=float, default=100,
                        help='Exit with a status of 2 if the total coverage is '
                             'less than MIN.')
    parser.add_argument('--max-wait', type=int, default=5,
                        help='Maximum time, in minutes, to wait for Coveralls '
                             'data. Defaults to 5.')
    parser.add_argument('--parallel-build-number', type=int,
                        help='The build number, eg $TRAVIS_BUILD_NUMBER.')
    parser.add_argument('--repo-token',
                        help='Required if --parallel-build-number is used and '
                             'should be the token use when POSTing back to '
                             'coveralls to mark the parallel build as done. '
                             'Should come from a secret.')
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()

    ensure_parallel_done(args)

    get_coverage_ = decorate(get_coverage, args)
    covered = get_coverage_(args.commit)
    if covered is None:
        print('No coverage information available for {}'.format(args.commit))
        sys.exit(1)
    elif covered < args.fail_under:
        message(args, covered, 'Failed coverage check for {} as {} < {}')
        sys.exit(2)
    else:
        message(args, covered, 'Coverage OK for {} as {} >= {}')

