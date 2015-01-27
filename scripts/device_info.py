#!/usr/bin/env python

import logging
import re
import subprocess
import time

from ncd_usb import set_relay

log = logging.getLogger()
logging.basicConfig(level=logging.INFO)


class DeviceError(Exception):
    pass


class TouchDevice(object):
    def __init__(self, devtype, serial, relay_url=None, bank=None,
                 power_pin=None, volume_down_pin=None, volume_up_pin=None):
        self.devtype = devtype
        self.serial = serial
        self.relay_url = relay_url
        self.bank = bank
        self.power_pin = power_pin
        self.volume_down_pin = volume_down_pin
        self.volume_up_pin = volume_up_pin

    def get_serial(self):
        return self.serial

    def get_state(self):
        """
        Check adb and fastboot to determine the state a device is in.
        Possible return values are:
            device, recovery, unknown, bootloader, disconnected
        """
        pattern = "{}\t(.+)\n".format(self.serial)
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

    def check_adb_shell(self):
        # Run a quick command in adb to see if the device is responding
        # subprocess will handle raising an exception if anything
        # goes wrong
        subprocess.check_call(['timeout', '10', 'adb', '-s',
                               self.serial, 'shell', 'pwd'])

    def reimage_from_fastboot(self):
        #Starting from fastboot mode, put a known-good image on the device
        log.info("Flashing the last stable image")
        subprocess.check_output(['ubuntu-device-flash', 'touch', '--serial',
                                 self.serial, '--channel',
                                 'ubuntu-touch/stable', '--bootstrap',
                                 '--developer-mode',
                                 '--password', '0000'])
        return self.wait_for_device(600)

    def wait_for_fastboot(self, timeout=120):
        if timeout > 10:
            wait = 10
        else:
            wait = timeout
        waited = 0
        while waited < timeout:
            state = self.get_state()
            if state == 'fastboot':
                return 0
            time.sleep(wait)
            waited += wait
        else:
            state = self.get_state()
            if state == 'fastboot':
                return 0
            log.error("Timed out waiting for fastboot. Recover device "
                      "manually")
            raise DeviceError("Device in state: {0}, still not available "
                              "after {1} seconds".format(state, timeout))

    def wait_for_device(self, timeout=120):
        # Wait for the device to come up to a good/booted state
        log.info("Waiting for the device to become available")
        try:
            subprocess.check_call(['timeout', str(timeout), 'adb', '-s',
                                  self.serial, 'wait-for-device'])
        except:
            log.error("Timed out waiting for device.")
            raise
        dev_state = self.get_state()
        if dev_state != 'device':
            log.error("Device in state: {0}, still not available after "
                      "{1} seconds".format(dev_state, timeout))
            raise DeviceError("Timed out waiting for device to respond after "
                              "{1} seconds".format(dev_state, timeout))
        else:
            log.info("Device is now available")
            return 0

    def force_bootloader(self):
        bootloader_func = getattr(
            self, '_{}_to_bootloader'.format(self.devtype))
        if bootloader_func and callable(bootloader_func):
            bootloader_func()
        else:
            raise DeviceError("Full recovery not possible with this device")

    def _krillin_to_bootloader(self):
        log.info("Forcing the device to enter the bootloader")
        #Power off the device from any state
        set_relay(self.relay_url, self.bank, self.power_pin, 1)
        set_relay(self.relay_url, self.bank, self.volume_down_pin, 1)
        set_relay(self.relay_url, self.bank, self.volume_up_pin, 1)
        time.sleep(16)
        set_relay(self.relay_url, self.bank, self.power_pin, 0)
        time.sleep(6)
        set_relay(self.relay_url, self.bank, self.volume_down_pin, 0)
        set_relay(self.relay_url, self.bank, self.volume_up_pin, 0)

    def _flo_to_bootloader(self):
        log.info("Forcing the device to enter the bootloader")
        #Power off the device from any state
        set_relay(self.relay_url, self.bank, self.power_pin, 1)
        time.sleep(12)
        set_relay(self.relay_url, self.bank, self.power_pin, 0)
        time.sleep(10)
        set_relay(self.relay_url, self.bank, self.volume_down_pin, 1)
        set_relay(self.relay_url, self.bank, self.power_pin, 1)
        time.sleep(5)
        set_relay(self.relay_url, self.bank, self.power_pin, 0)
        time.sleep(1)
        set_relay(self.relay_url, self.bank, self.volume_down_pin, 0)

    def _mako_to_bootloader(self):
        log.info("Forcing the device to enter the bootloader")
        #Power off the device from any state
        set_relay(self.relay_url, self.bank, self.power_pin, 1)
        time.sleep(12)
        set_relay(self.relay_url, self.bank, self.power_pin, 0)
        time.sleep(10)
        #Enter the bootloader
        set_relay(self.relay_url, self.bank, self.volume_down_pin, 1)
        set_relay(self.relay_url, self.bank, self.power_pin, 1)
        time.sleep(5)
        set_relay(self.relay_url, self.bank, self.volume_down_pin, 0)
        set_relay(self.relay_url, self.bank, self.power_pin, 0)


# When looking at the relay webUI for the mapping, we consider all
# ports and banks to start numbering from 0
DEVICES = {
    "krillin-01": TouchDevice("krillin", "JB011018"),
    "krillin-02": TouchDevice("krillin", "JB010894"),
    "krillin-03": TouchDevice("krillin", "JB015156",
                              relay_url="http://ferris.ubuntu-ci",
                              bank=2, power_pin=0, volume_up_pin=1,
                              volume_down_pin=2),
    "krillin-04": TouchDevice("krillin", "JB006885",
                              relay_url="http://ferris.ubuntu-ci",
                              bank=1, power_pin=4, volume_up_pin=5,
                              volume_down_pin=6),
    "krillin-05": TouchDevice("krillin", "JB015256"),
    "krillin-06": TouchDevice("krillin", "JW010687"),
    "krillin-07": TouchDevice("krillin", "JW011999",
                              relay_url="http://ferris.ubuntu-ci",
                              bank=2, power_pin=4, volume_up_pin=5,
                              volume_down_pin=6),
    "krillin-08": TouchDevice("krillin", "JW013513",
                              relay_url="http://ferris.ubuntu-ci",
                              bank=1, power_pin=0, volume_up_pin=1,
                              volume_down_pin=2),
    "krillin-09": TouchDevice("krillin", "JW010053",
                              relay_url="http://ferris.ubuntu-ci",
                              bank=0, power_pin=4, volume_up_pin=5,
                              volume_down_pin=6),
    "krillin-10": TouchDevice("krillin", "JB012976",
                              relay_url="http://decatur.ubuntu-ci",
                              bank=2, power_pin=0, volume_up_pin=1,
                              volume_down_pin=2),
    "ps-mako-01": TouchDevice("mako", "0090f741e3d141bc"),
    "ps-mako-02": TouchDevice("mako", "04ccca120acd4dea"),
    "ps-mako-03": TouchDevice("mako", "04cb53b598546534"),
    "ps-mako-04": TouchDevice("mako", "04cbcc545f5328a5"),
    "mako-01": TouchDevice("mako", "01aa3d7a5dcba4a2"),
    "mako-02": TouchDevice("mako", "01ade38b552014d4"),
    "mako-03": TouchDevice("mako", "04c6714ed7c863f2"),
    "mako-04": TouchDevice("mako", "04df89cf0f9d0933",
                           relay_url="http://qa-relay-control.ubuntu-ci",
                           bank=1, power_pin=4, volume_down_pin=5),
    "mako-05": TouchDevice("mako", "01b22f82dc5cec63",
                           relay_url="http://decatur.ubuntu-ci",
                           bank=0, power_pin=0, volume_down_pin=1),
    "mako-06": TouchDevice("mako", "04ed70928fdc13ba",
                           relay_url="http://decatur.ubuntu-ci",
                           bank=0, power_pin=2, volume_down_pin=3),
    "mako-07": TouchDevice("mako", "01e2f64788556934",
                           relay_url="http://decatur.ubuntu-ci",
                           bank=0, power_pin=4, volume_down_pin=5),
    "mako-08": TouchDevice("mako", "04ea16a163930769",
                           relay_url="http://decatur.ubuntu-ci",
                           bank=0, power_pin=6, volume_down_pin=7),
    "mako-09": TouchDevice("mako", "04fda12ea08fe3c7"),
    "mako-10": TouchDevice("mako", "01ce848e48dfa6a2"),
    "mako-11": TouchDevice("mako", "04ed727c929709ba"),
    #If looking at the LAB wiki page, subtract 1 from the bank and pin numbers
    #from what it says on the wiki (our numbers start at 0)
    "mako-12": TouchDevice("mako", "00693fd555c9186a",
                           relay_url="http://qa-relay-control.ubuntu-ci",
                           bank=0, power_pin=1, volume_down_pin=2),
    "mako-13": TouchDevice("mako", "0084e99c5315731b",
                           relay_url="http://qa-relay-control.ubuntu-ci",
                           bank=0, power_pin=3, volume_down_pin=4),
    "mako-14": TouchDevice("mako", "007c6d84d348838e",
                           relay_url="http://qa-relay-control.ubuntu-ci",
                           bank=0, power_pin=5, volume_down_pin=6),
    "mako-15": TouchDevice("mako", "00763b4a61ce0f87",
                           relay_url="http://qa-relay-control.ubuntu-ci",
                           bank=1, power_pin=0, volume_down_pin=1),
    "mako-16": TouchDevice("mako", "017121eacf5282c4",
                           relay_url="http://qa-relay-control.ubuntu-ci",
                           bank=1, power_pin=2, volume_down_pin=3),
    #mako-17 has a broken screen but should work, on ashes
    "mako-17": TouchDevice("mako", "04e0d2f6d3cab77d"),
    "mako-18": TouchDevice("mako", "027b981a4c1110dd",
                           relay_url="http://decatur.ubuntu-ci",
                           bank=1, power_pin=0, volume_down_pin=1),
    "mako-19": TouchDevice("mako", "021c8cdfd5d38602"),
    "mako-20": TouchDevice("mako", "05083705e0d29402",
                           relay_url="http://decatur.ubuntu-ci",
                           bank=1, power_pin=2, volume_down_pin=3),
    "mako-fginther": TouchDevice("mako", "04c3c2be1d5248b3"),
    "ps-manta-01": TouchDevice("manta", "R32D203DDZR"),
    "manta-01": TouchDevice("manta", "R32D102RPZL"),
    "manta-02": TouchDevice("manta", "R32D102RPPK"),
    "manta-03": TouchDevice("manta", "R32D200N4YH"),
    "manta-05": TouchDevice("manta", "R32D203DMBY"),  # Out of lab for now
    "flo-01": TouchDevice("flo", "09f306dc"),
    "flo-02": TouchDevice("flo", "08dbee36"),
    "flo-03": TouchDevice("flo", "09d55fa8"),
    "flo-04": TouchDevice("flo", "09e68682"),
    "flo-05": TouchDevice("flo", "0a22f7cf",
                          relay_url="http://ferris.ubuntu-ci",
                          bank=0, power_pin=0, volume_down_pin=2),
    "flo-06": TouchDevice("flo", "08f09bb0"),
}


def get_device(name):
    # This raises KeyError if we don't have any record of that device
    return DEVICES[name]
