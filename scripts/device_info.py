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
    "mako-05": TouchDevice("mako", "01b22f82dc5cec63"),
    "mako-06": TouchDevice("mako", "04ed70928fdc13ba"),
    "mako-07": TouchDevice("mako", "01e2f64788556934"),
    "mako-08": TouchDevice("mako", "04ea16a163930769"),
    "mako-10": TouchDevice("mako", "01ce848e48dfa6a2"),
    "mako-11": TouchDevice("mako", "04ed727c929709ba"),
    "mako-12": TouchDevice("mako", "00693fd555c9186a",
                           relay_url="http://qa-relay-control.ubuntu-ci",
                           bank=0, power_pin=1, volume_pin=2),
    "manta-01": TouchDevice("manta", "R32D102RPZL"),
    "manta-02": TouchDevice("manta", "R32D102RPPK"),
    "manta-04": TouchDevice("manta", "R32D203DDZR"),
    "manta-05": TouchDevice("manta", "R32D203DMBY"),
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
