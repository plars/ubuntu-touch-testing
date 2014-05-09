#!/usr/bin/env python

import device_info
import logging
import subprocess
import sys
import time
from ncd_usb import set_relay

log = logging.getLogger()
logging.basicConfig(level=logging.INFO)


class DeviceError(Exception):
    pass


def _reimage_from_fastboot(serial):
    #Starting from fastboot mode, put a known-good image on the device
    log.info("Flashing the last stable image")
    subprocess.check_output(['ubuntu-device-flash', '--serial', serial,
                             '--channel', 'ubuntu-touch/stable',
                             '--bootstrap'])
    return _wait_for_device(serial, 600)


def _wait_for_device(serial, timeout=120):
    # Wait for the device to come up to a good/booted state
    log.info("Waiting for the device to become available")
    try:
        subprocess.check_call(['timeout', str(timeout), 'adb', '-s',
                               serial, 'wait-for-device'])
    except:
        log.error("Timed out waiting for reboot. Recover device manually")
        raise
    dev_state = device_info.get_state(serial)
    if dev_state != 'device':
        raise DeviceError("Device in state: {0}, still not available after "
                          "{1} seconds".format(dev_state, timeout))
    else:
        log.info("Device is now available")
        return 0


def _wait_for_fastboot(serial, timeout=120):
    if timeout > 10:
        wait = 10
    else:
        wait = timeout
    waited = 0
    while waited < timeout:
        state = device_info.get_state(serial)
        if state == 'fastboot':
            return 0
        time.sleep(wait)
        waited += wait
    else:
        state = device_info.get_state(serial)
        if state == 'fastboot':
            return 0
        log.error("Timed out waiting for fastboot. Recover device manually")
        raise DeviceError("Device in state: {0}, still not available after "
                          "{1} seconds".format(state, timeout))


def _mako_to_bootloader(urlbase, bank, power=1, volume=2):
    """
    This just works on mako for certain, but that's all we have connected
    right now. After this runs, the device should be in the bootloader
    """
    log.info("Forcing the device to enter the bootloader")
    #Power off the device from any state
    set_relay(urlbase, bank, power, 1)
    time.sleep(10)
    set_relay(urlbase, bank, power, 0)
    time.sleep(10)
    #Enter the bootloader
    set_relay(urlbase, bank, volume, 1)
    set_relay(urlbase, bank, power, 1)
    time.sleep(5)
    set_relay(urlbase, bank, volume, 0)
    set_relay(urlbase, bank, power, 0)


def _full_recovery(device_name):
    #we only support mako at the moment
    (url, bank, power, volume) = device_info.get_power(device_name)
    if None in (url, bank, power, volume):
        #This device does not have information about relays
        raise DeviceError("Full recovery not possible with this device")
    _mako_to_bootloader(url, bank, power, volume)
    serial = device_info.get_serial(device_name)
    _wait_for_fastboot(serial)
    _reimage_from_fastboot(serial)


def recover(device):
    try:
        serial = device_info.get_serial(device)
    except AttributeError:
        log.error("No device found for '{}'".format(device))
        raise
    state = device_info.get_state(serial)
    if state in ('device', 'recovery'):
        #The device can proceed with testing
        return 0
    if state == 'fastboot':
        #The device is in fastboot right now, we need it booted first
        return _reimage_from_fastboot(serial)
    if state == 'unknown':
        #The device is in an unknown state, we need full recovery
        return _full_recovery(device)
    #In theory, we should never get here, but....
    raise DeviceError("Device '{}' is in an unknown state!".format(device))


if __name__ == '__main__':
    name = sys.argv[1]
    try:
        print(recover(name))
    except AttributeError:
        #This is what we'll get if it's an unknown device, raise for
        #everything else so we get better debugging information
        sys.exit(-1)
