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

import testconfig


class APTest(testconfig.Test):
    def __init__(self, name, app=None, pkgs=None):
        testconfig.Test.__init__(self, name)
        self.pkgs = pkgs
        if not app:
            # convert share-app-autopilot to share_app
            app = name.replace('-', '_').replace('_autopilot', '')
        self.app = app


TESTSUITES = [
    APTest('friends-app-autopilot', pkgs=['friends-app-autopilot']),
    APTest('mediaplayer-app-autopilot', pkgs=['mediaplayer-app-autopilot']),
    APTest('gallery-app-autopilot', pkgs=['gallery-app-autopilot']),
    APTest('webbrowser-app-autopilot', pkgs=['webbrowser-app-autopilot']),
    APTest('unity8-autopilot', 'unity8', pkgs=['python-gi']),
    APTest('notes-app-autopilot'),
    APTest('camera-app-autopilot', pkgs=['camera-app-autopilot']),
    APTest('dialer-app-autopilot', pkgs=['dialer-app-autopilot']),
    APTest('messaging-app-autopilot', pkgs=['messaging-app-autopilot']),
    APTest('address-book-app-autopilot', pkgs=['address-book-app-autopilot']),
    APTest('calendar-app-autopilot'),
    APTest('music-app-autopilot'),
    APTest('dropping-letters-app-autopilot'),
    APTest('ubuntu-calculator-app-autopilot'),
    APTest('ubuntu-clock-app-autopilot'),
    APTest('ubuntu-filemanager-app-autopilot'),
    APTest('ubuntu-rssreader-app-autopilot'),
    APTest('ubuntu-terminal-app-autopilot'),
    APTest('ubuntu-weather-app-autopilot'),
    APTest('ubuntu-ui-toolkit-autopilot', 'ubuntuuitoolkit',
           ['ubuntu-ui-toolkit-autopilot']),
    APTest('ubuntu-system-settings-online-accounts-autopilot',
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
