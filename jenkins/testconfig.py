#!/usr/bin/env python

# Ubuntu Testing Automation Harness
# Copyright 2013 Canonical Ltd.

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse

DEF_FMT = '{prefix}{series}-{imagetype}-{type}-smoke-{testname}'
IDLE_FMT = '{prefix}{testname}-{series}-{imagetype}-armhf-install-idle-{type}'


class Test(object):
    def __init__(self, name, fmt=DEF_FMT, ap=False):
        self.name = name
        self.fmt = fmt
        self.ap = ap


TESTSUITES_PRE = [
    Test('install-and-boot'),
    Test('default'),
]
TESTSUITES_POST = [
    Test('click_image_tests'),
    Test('sdk'),
    Test('security'),
    Test('eventstat', IDLE_FMT),
    Test('smem', IDLE_FMT),
    Test('memevent',
         '{prefix}{testname}-{series}-{imagetype}-armhf-default-{type}'),
]
TESTSUITES = TESTSUITES_PRE + TESTSUITES_POST


def _handle_tests(args):
    tests = [t.name for t in TESTSUITES]
    print(' '.join(tests))


def _get_parser():
    parser = argparse.ArgumentParser(
        description='List information on configured UTAH tests for touch')
    sub = parser.add_subparsers(title='Commands', metavar='')

    p = sub.add_parser('tests', help='List tests by CI test name')
    p.set_defaults(func=_handle_tests)

    return parser


def main():
    args = _get_parser().parse_args()
    return args.func(args)

if __name__ == '__main__':
    exit(main())
