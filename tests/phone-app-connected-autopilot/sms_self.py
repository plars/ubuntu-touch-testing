#!/usr/bin/env python

import argparse
import dbus


def _get_parser():
    parser = argparse.ArgumentParser(
        description='Send an SMS message to yourself via the ofono API')
    parser.add_argument('-m', '--modem', default='/ril_0',
                        help='The modem to use. Default: %(default)s')
    parser.add_argument('message', nargs='?', default='hello world',
                        help='Message to send. Default "%(default)s"')
    parser.add_argument('--list', action='store_true',
                        help='Just print the number of this cell phone.')
    return parser


def _main(args):
    bus = dbus.SystemBus()
    obj = bus.get_object('org.ofono', args.modem)

    mgr = dbus.Interface(obj, 'org.ofono.SimManager')
    local_sms = str(mgr.GetProperties()['SubscriberNumbers'][0])

    if args.list:
        print local_sms
    else:
        mgr = dbus.Interface(obj, 'org.ofono.MessageManager')
        mgr.SendMessage(local_sms, args.message)


if __name__ == '__main__':
    _main(_get_parser().parse_args())
