#! /usr/bin/python

"""A utility to control the USB relay's in the QA lab."""

import argparse
import sys
import urllib2


def set_relay(urlbase, bank, relay, on):
    # the values 100/108 came from the JavaScript of our web-based management
    # system for the relays. The meaning of the values isn't documented.
    if on:
        relay += 108
    else:
        relay += 100
    cmd = '254,{},{}'.format(relay, bank + 1)
    url = '{}/cgi-bin/runcommand.sh?1:cmd={}'.format(urlbase, cmd)
    resp = urllib2.urlopen(url)
    resp = resp.read()
    if 'OK' not in resp:
        print('ERROR: bad response: {}'.format(resp))
        sys.exit(1)


def _get_parser():
    parser = argparse.ArgumentParser(
        description='Toggles an NCD relay connected to a USB cable on/off')
    parser.add_argument('-u', '--url',
                        default='http://qa-relay-control.ubuntu-ci',
                        help='NCD relay URL. default=%(default)s')
    parser.add_argument('-b', '--bank', type=int, required=True,
                        help='NCD relay 0-based bank ID.')
    parser.add_argument('-r', '--relay', type=int, required=True,
                        help='NCD relay 0-based relay ID.')
    parser.add_argument('action', metavar='action',
                        choices=('on', 'off'),
                        help='action to perform on|off')
    return parser


if __name__ == '__main__':
    args = _get_parser().parse_args()

    # NOTE: when the relay is ON usb is actually OFF. ie the logic
    # is backwards between them, thus action=off actually turns
    # the relay on
    set_relay(args.url, args.bank, args.relay, args.action == 'off')
