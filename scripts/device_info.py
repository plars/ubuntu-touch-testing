#!/usr/bin/env python

import re
import subprocess


class TouchDevice(object):
    def __init__(self, devtype, serial, relay_url=None, bank=None,
                 power_pin=None, volume_pin=None):
        self.devtype = devtype
        self.serial = serial
        self.relay_url = relay_url
        self.bank = bank
        self.power_pin = power_pin
        self.volume_pin = volume_pin

DEVICES = {
    "ps-mako-01": TouchDevice("mako", "0090f741e3d141bc"),
    "ps-mako-04": TouchDevice("mako", "04cbcc545f5328a5"),
    "mako-01": TouchDevice("mako", "01aa3d7a5dcba4a2"),
    "mako-02": TouchDevice("mako", "01ade38b552014d4"),
    "mako-03": TouchDevice("mako", "04c6714ed7c863f2"),
    "mako-04": TouchDevice("mako", "04df89cf0f9d0933"),
    "mako-05": TouchDevice("mako", "01b22f82dc5cec63"),
    "mako-06": TouchDevice("mako", "04ed70928fdc13ba"),
    "mako-07": TouchDevice("mako", "01e2f64788556934"),
    "mako-08": TouchDevice("mako", "04ea16a163930769"),
    "mako-09": TouchDevice("mako", "04fda12ea08fe3c7"),
    "mako-10": TouchDevice("mako", "01ce848e48dfa6a2"),
    "mako-11": TouchDevice("mako", "04ed727c929709ba"),
    #If looking at the LAB wiki page, subtract 1 from the bank and pin numbers
    #from what it says on the wiki (our numbers start at 0)
    "mako-12": TouchDevice("mako", "00693fd555c9186a",
                           relay_url="http://qa-relay-control.ubuntu-ci",
                           bank=0, power_pin=1, volume_pin=2),
    "mako-13": TouchDevice("mako", "0084e99c5315731b",
                           relay_url="http://qa-relay-control.ubuntu-ci",
                           bank=0, power_pin=3, volume_pin=4),
    "mako-14": TouchDevice("mako", "007c6d84d348838e",
                           relay_url="http://qa-relay-control.ubuntu-ci",
                           bank=0, power_pin=5, volume_pin=6),
    "mako-15": TouchDevice("mako", "00763b4a61ce0f87",
                           relay_url="http://qa-relay-control.ubuntu-ci",
                           bank=1, power_pin=0, volume_pin=1),
    "mako-16": TouchDevice("mako", "017121eacf5282c4",
                           relay_url="http://qa-relay-control.ubuntu-ci",
                           bank=1, power_pin=2, volume_pin=3),
    #mako-17 has a broken screen but should work, on ashes
    "mako-17": TouchDevice("mako", "04e0d2f6d3cab77d"),
    "ps-manta-01": TouchDevice("manta", "R32D203DDZR"),
    "manta-01": TouchDevice("manta", "R32D102RPZL"),
    "manta-02": TouchDevice("manta", "R32D102RPPK"),
    "manta-03": TouchDevice("manta", "R32D200N4YH"),
    "manta-05": TouchDevice("manta", "R32D203DMBY"),  # Out of lab for now
    "flo-01": TouchDevice("flo", "09f306dc"),
    "flo-02": TouchDevice("flo", "08dbee36"),
    "flo-03": TouchDevice("flo", "09d55fa8"),
}


def get_state(serial):
    """
    Check adb and fastboot to determine the state a device is in.
    Possible return values are:
        device, recovery, unknown, bootloader, disconnected
    """
    pattern = "{}\t(.+)\n".format(serial)
    adb_devices = subprocess.check_output(['adb', 'devices'])
    found = re.search(pattern, adb_devices)
    if not found:
        #Otherwise, check fastboot
        fastboot_devices = subprocess.check_output(['fastboot', 'devices'])
        found = re.search(pattern, fastboot_devices)
    if found:
        state = found.group(1)
        return state
    else:
        return 'disconnected'


def get_serial(name):
    return DEVICES.get(name).serial


def get_power(name):
    device = DEVICES.get(name)
    return (device.relay_url, device.bank, device.power_pin, device.volume_pin)
