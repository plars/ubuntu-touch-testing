#!/usr/bin/env python

import device_info
import logging
import os
import requests
import sys
import time
import yaml

from phabletutils.environment import detect_device

log = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def _full_recovery(device):
    try:
        device.force_bootloader()
    except:
        #This device does not have information about relays
        _offline_device()
        raise
    try:
        device.wait_for_fastboot()
        device.reimage_from_fastboot()
    except:
        _offline_device()
        raise
    try:
        device.check_adb_shell()
    except:
        # The device looks like it's available, but not responding
        _offline_device()
        raise device_info.DeviceError("Could not fully recover device")
    return 0


def _get_jenkins_creds(url):
    try:
        home = os.environ.get('HOME')
        credpath = os.path.join(home, '.ubuntu-ci/jenkins-keys.yaml')
        with open(credpath) as credfile:
            creds = yaml.load(credfile.read())
        jenkins = creds.get(url)
        user = jenkins.get('user')
        key = jenkins.get('key')
    except (AttributeError, IOError):
        user = None
        key = None
    return (user, key)


def _offline_device():
    # It's unlikely the node name will be different, but just in case
    node = os.environ.get('NODE_NAME', None)
    host = os.environ.get('JENKINS_URL', None)
    (user, key) = _get_jenkins_creds(host)
    if not (user and key and host and node):
        log.warn("Unable to mark device offline automatically")
        return
    url = "{}/computer/{}/toggleOffline".format(host, node)
    param_data = {'offlineMessage': 'unrecoverable'}
    delay = 2
    # Retry with exponential delay from 1 to 128 seconds
    # This will retry for no longer than 4 min 15 sec before failing
    for attempt in range(8):
        time.sleep(delay ** attempt)
        try:
            response = requests.post(url, params=param_data, auth=(user, key))
        except Exception as exc:
            log.exception('Error contacting jenkins: {}'.format(exc.message))
            continue
        if response.status_code != 200:
            log.warn("Error marking {} offline, retrying".format(node))
        else:
            log.info("{} has been marked offline".format(node))
            return
    log.error("Fatal error marking {} offline".format(node))


def get_device_type():
    device_type = os.environ.get('DEVICE_TYPE')
    if device_type is None:
        device_type = detect_device(None)


def recover(device_name):
    try:
        device = device_info.get_device(device_name)
    except KeyError:
        log.error("No device found for '{}'".format(device_name))
        raise
    state = device.get_state()
    if state in ('device'):
        try:
            device.check_adb_shell()
            # XXX psivaa 10/09/2015 We've seen instances when detect_device throwing
            # detect_device throwing exceptions even when adb_shell works OK
            # recover it fully in such a situation
            get_device_type()
        except:
            # The device looks like it's available, but not responding
            return _full_recovery(device)
        #The device can proceed with testing
        return 0
    if state == 'recovery':
        try:
            device.reboot()
            device.wait_for_device()
            device.check_adb_shell()
            return 0
        except:
            return _full_recovery(device)
    if state == 'fastboot':
        #The device is in fastboot right now, we need it booted first
        try:
            device.reimage_from_fastboot()
            device.check_adb_shell()
            return 0
        except:
            # The device looks like it's available, but not responding
            return _full_recovery(device)
    if state in ('offline', 'unknown', 'disconnected'):
        #The device is in an unknown state, we need full recovery
        return _full_recovery(device)
    #In theory, we should never get here, but....
    _offline_device()
    raise device_info.DeviceError(
        "Device '{}' is in an unknown state!".format(device_name))


if __name__ == '__main__':
    name = sys.argv[1]
    try:
        print(recover(name))
    except AttributeError:
        #This is what we'll get if it's an unknown device, raise for
        #everything else so we get better debugging information
        sys.exit(-1)
