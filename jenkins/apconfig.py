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
import collections

TestSuite = collections.namedtuple('TestSuite', ['name', 'app', 'pkgs'])


def _ap_test(name, app=None, pkgs=None):
    if not app:
        # convert share-app-autopilot to share_app
        app = name.replace('-', '_').replace('_autopilot', '')
    return TestSuite(name, app, pkgs)


TESTSUITES = [
    _ap_test('friends-app-autopilot', pkgs=['friends-app-autopilot']),
    _ap_test('mediaplayer-app-autopilot', pkgs=['mediaplayer-app-autopilot']),
    _ap_test('gallery-app-autopilot', pkgs=['gallery-app-autopilot']),
    _ap_test('webbrowser-app-autopilot', pkgs=['webbrowser-app-autopilot']),
    _ap_test('unity8-autopilot', 'unity8'),
    _ap_test('notes-app-autopilot'),
    _ap_test('camera-app-autopilot', pkgs=['camera-app-autopilot']),
    _ap_test('dialer-app-autopilot', pkgs=['dialer-app-autopilot']),
    _ap_test('messaging-app-autopilot', pkgs=['messaging-app-autopilot']),
    _ap_test('address-book-app-autopilot',
             pkgs=['address-book-app-autopilot']),
    _ap_test('calendar-app-autopilot', pkgs=['python-dateutil']),
    _ap_test('music-app-autopilot', pkgs=['python-mock']),
    _ap_test('dropping-letters-app-autopilot'),
    _ap_test('ubuntu-calculator-app-autopilot'),
    _ap_test('ubuntu-clock-app-autopilot'),
    _ap_test('ubuntu-filemanager-app-autopilot'),
    _ap_test('ubuntu-rssreader-app-autopilot'),
    _ap_test('ubuntu-terminal-app-autopilot'),
    _ap_test('ubuntu-weather-app-autopilot'),
    _ap_test('ubuntu-ui-toolkit-autopilot', 'ubuntuuitoolkit',
             ['ubuntu-ui-toolkit-autopilot']),
    _ap_test('ubuntu-system-settings-online-accounts-autopilot',
             'online_accounts_ui',
             ['ubuntu-system-settings-online-accounts-autopilot']),
]


def _handle_packages(args):
    pkgs = []
    for suite in TESTSUITES:
        if not args.app or suite.app in args.app:
            if suite.pkgs:
                pkgs.extend(suite.pkgs)
    print(' '.join(pkgs))
    return 0


def _handle_apps(args):
    apps = [t.app for t in TESTSUITES]
    print(' '.join(apps))


def _handle_tests(args):
    tests = [t.name for t in TESTSUITES]
    print(' '.join(tests))


def _get_parser():
    parser = argparse.ArgumentParser(
        description='List information on configured autopilot tests for touch')
    sub = parser.add_subparsers(title='Commands', metavar='')

    p = sub.add_parser('packages', help='List packages required for apps')
    p.set_defaults(func=_handle_packages)
    p.add_argument('-a', '--app', action='append',
                   help='Autopilot test application. eg share_app')

    p = sub.add_parser('apps', help='List tests by autopilot application name')
    p.set_defaults(func=_handle_apps)

    p = sub.add_parser('tests', help='List tests by CI test name')
    p.set_defaults(func=_handle_tests)

    return parser


def main():
    args = _get_parser().parse_args()
    return args.func(args)

if __name__ == '__main__':
    exit(main())
