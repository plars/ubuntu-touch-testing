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
    def __init__(self, name, fmt=DEF_FMT):
        self.name = name
        self.fmt = fmt


class APTest(Test):
    def __init__(self, name, app=None, pkgs=None):
        Test.__init__(self, name)
        self.pkgs = pkgs
        if not app:
            # convert share-app-autopilot to share_app
            app = name.replace('-', '_').replace('_autopilot', '')
        self.app = app


TESTSUITES = [
    Test('install-and-boot'),
    Test('default'),
]
TESTSUITES += [
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
TESTSUITES += [
    Test('click_image_tests'),
    Test('sdk'),
    Test('security'),
    Test('eventstat', IDLE_FMT),
    Test('smem', IDLE_FMT),
    Test('memevent',
         '{prefix}{testname}-{series}-{imagetype}-armhf-default-{type}'),
]


def filter_tests(tests, image_type):
    if image_type:
        func = globals().get('get_tests_%s' % image_type)
        if func:
            tests = func(tests)
        elif image_type not in ['touch', 'touch_mir']:
            print('Unsupported image type: %s' % image_type)
            exit(1)
    return tests


def _get_tests(test_type, image_type):
    tests = [t for t in TESTSUITES if type(t) == test_type]
    return filter_tests(tests, image_type)


def _handle_utah(args):
    tests = _get_tests(Test, args.image_type)
    # NOTE: this is only called by MEGA jobs, so we can skip install-and-boot
    print(' '.join([t.name for t in tests if t.name != 'install-and-boot']))


def _handle_ap_apps(args):
    tests = _get_tests(APTest, args.image_type)
    print(' '.join([t.app for t in tests]))


def _handle_ap_packages(args):
    pkgs = []
    tests = _get_tests(APTest, args.image_type)
    for test in tests:
        if not args.app or test.app in args.app:
            if test.pkgs:
                pkgs.extend(test.pkgs)
    print(' '.join(pkgs))


def get_tests_touch_sf4p(common_tests):
    tests = []
    test_set = [
        'install-and-boot',
        'default',
        'unity8-autopilot',
    ]

    tests = [t for t in common_tests if t.name in test_set]
    return tests


def get_tests_touch_custom(common_tests):
    tests = []
    test_set = [
        'install-and-boot',
        'default',
        'unity8-autopilot',
        'webbrowser-app-autopilot',
    ]

    tests = [t for t in common_tests if t.name in test_set]
    tests.insert(1, Test('customizations'))
    return tests


def _get_parser():
    parser = argparse.ArgumentParser(
        description='List information on configured tests for touch')
    sub = parser.add_subparsers(title='Commands', metavar='')

    p = sub.add_parser('utah', help='List UTAH tests')
    p.set_defaults(func=_handle_utah)
    p.add_argument('-i', '--image-type',
                   help='Return list of test configured for an image type.')

    p = sub.add_parser('apps', help='List autopilot application names')
    p.set_defaults(func=_handle_ap_apps)
    p.add_argument('-i', '--image-type',
                   help='Return list of test configured for an image type.')

    p = sub.add_parser('packages', help='List packages required for autopilot')
    p.set_defaults(func=_handle_ap_packages)
    g = p.add_mutually_exclusive_group()
    g.add_argument('-i', '--image-type',
                   help='''If no apps are listed, limit to tests for an
                        image type.''')
    g.add_argument('-a', '--app', action='append',
                   help='Autopilot test application. eg share_app')
    return parser


def main():
    args = _get_parser().parse_args()
    return args.func(args)

if __name__ == '__main__':
    exit(main())
