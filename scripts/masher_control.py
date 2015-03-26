#!/usr/bin/env python

"""A utility to control the uci-phone-masher controllers in the CI lab."""

import argparse
import json
import sys
import urllib
import urllib2


def set_button(urlbase, button, on):
    state = 'on' if on else 'off'
    data = {
        'state': state,
    }
    url = '{}/button/{}'.format(urlbase, button)
    try:
        resp = urllib2.urlopen(url, data=urllib.urlencode(data))
    except urllib2.URLError:
        print('ERROR: URL connection or read error: {}'.format(url))
        return -1

    try:
        resp = resp.read()
        json_resp = json.loads(resp)
    except (urllib2.URLError, ValueError):
        print('ERROR: bad response: {}'.format(resp))
        return -1

    if not json_resp.get('button_states', None) == state:
        print('ERROR: unexpected response: {}'.format(resp))
        return -1


def _get_parser():
    parser = argparse.ArgumentParser(
        description='Toggles a button connected to a uci-phone-masher on/off')
    parser.add_argument('-u', '--url',
                        default='http://ci-phone-masher.ubuntu-ci',
                        help='Phone Masher controller. default=%(default)s')
    parser.add_argument('-b', '--button', type=int, required=True,
                        help='The uci-phone-master button ID.')
    parser.add_argument('action', metavar='action',
                        choices=('on', 'off'),
                        help='Action to perform on|off')
    return parser


if __name__ == '__main__':
    args = _get_parser().parse_args()

    sys.exit(set_button(args.url, args.button, args.action == 'on'))
