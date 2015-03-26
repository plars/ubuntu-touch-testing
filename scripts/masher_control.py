#!/usr/bin/env python

"""A utility to control the uci-phone-masher controllers in the CI lab."""

import argparse
import json
import sys
import urllib
import urllib2


def set_button(urlbase, button, on):
    '''Set the desired button to on for any non-false value of "on"'''
    state = 'on' if on else 'off'
    data = {
        'state': state,
    }
    url = '{}/button/{}'.format(urlbase, button)
    try:
        url_resp = urllib2.urlopen(url, data=urllib.urlencode(data))
    except urllib2.URLError as e:
        print('ERROR: URL connection or read error on {}: {}'.format(url, e))
        return -1

    try:
        content = url_resp.read()
    except urllib2.URLError as e:
        print('ERROR: URL read error on {}: {}'.format(url_resp, e))
        return -1

    try:
        json_resp = json.loads(content)
    except (urllib2.URLError, ValueError) as e:
        print('ERROR: json conversion failed on {}: {}'.format(content, e))
        return -1

    if not json_resp.get('button_states', None) == state:
        # This is a fail safe to make sure the controller attempted to set
        # the button to what was requested. If it fails, dump the original
        # content.
        print('ERROR: unexpected response: {}'.format(content))
        return -1

    return 0


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
