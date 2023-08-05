#!/usr/bin/env python

from __future__ import print_function, unicode_literals

import argparse
import json
try:
    from http.client import HTTPSConnection
except ImportError:
    from httplib import HTTPSConnection
import logging
import sys

from packaging.version import Version, InvalidVersion, _Version


VERSION = '1.2'

logger = logging.getLogger(__name__)


class UserError(Exception):
    pass


def debianize(pep440_version):
    try:
        parsed = Version(pep440_version)
    except InvalidVersion as e:
        raise UserError(
            "%s. See https://www.python.org/dev/peps/pep-0440/.\n"
            "Failed.\n" % (e,),
        )

    v = parsed._version._asdict()
    if v['pre']:
        # Hack version serialization: prepend '~' as pre version.
        v['pre'] = ('~',) + v['pre']
        parsed._version = _Version(**v)

    debian_version = str(parsed)
    # We can get two ~ in debian version, that's not a problem.
    debian_version = debian_version.replace('.dev', '~dev')

    return debian_version


ARGV, FILE, PYPI = range(3)


def parse_options(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-e', '--echo',
        action='store_true', dest='echo',
        help="Echo PEP440 version before debian."
    )
    parser.add_argument(
        '-f', '--file', '--stdin',
        action='store_const', const=FILE, dest='type_',
        help="Read version from file."
    )
    parser.add_argument(
        '-p', '--pypi',
        action='store_const', const=PYPI, dest='type_',
        help="Search version on PyPI."
    )
    parser.add_argument(
        'argument',
        default=None, nargs='?',
        metavar='VERSION | REQUIREMENT | FILE',
        help="Source of version to parse."
    )
    parser.set_defaults(type_=ARGV)
    options = parser.parse_args(argv)
    if options.type_ == ARGV and options.argument is None:
        parser.error("Missing version to translate!")
    return options


def read_version(type_, argument):
    if ARGV == type_:
        return argument
    elif FILE == type_:
        if argument in {'-', None}:
            return sys.stdin.readline().strip()

        with open(argument, 'r') as fo:
            return fo.readline().strip()
    elif PYPI == type_:
        logger.info("Querying pypi.python.org.")
        path = '/pypi/%s/json' % (argument,)

        for i in range(16):
            conn = HTTPSConnection("pypi.python.org")
            logger.debug("Query %s", path)
            conn.request('GET', path)
            res = conn.getresponse()
            if 301 == res.status:
                if hasattr(res, 'getheaders'):
                    headers = dict(res.getheaders())
                else:
                    headers = {k.lower(): v for k, v in res.headers.items()}
                path = headers['location']
                continue
            break
        else:
            raise UserError("Exceeded redirection limit.")

        if res.status != 200:
            raise UserError(
                "Failed to query PyPI: %s %s" % (res.status, res.reason)
            )

        payload = res.read().decode('utf-8')
        data = json.loads(payload)
        latest_version = data['info']['version']
        return latest_version
    else:
        raise Exception("Internal error: unknown argument type %s" % (type_,))


def main(argv=None):
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)-8s %(message)s",
    )
    try:
        options = parse_options(argv)
        pep440_version = read_version(options.type_, options.argument)
        debian_version = debianize(pep440_version)
        if options.echo:
            print(pep440_version, debian_version)
        else:
            print(debian_version)
    except UserError as e:
        logger.error("%s", e)
        sys.exit(1)


if '__main__' == __name__:
    main()
