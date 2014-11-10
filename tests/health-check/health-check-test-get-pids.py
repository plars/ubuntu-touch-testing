#!/usr/bin/python3

import os
import psutil
import platform

basedir = os.path.dirname(__file__)
default_threshold_path = os.path.join(
    os.path.join(basedir, 'thresholds'), platform.machine())

ignore_procs = [
    'health-check', 'init', 'cat', 'vi', 'emacs', 'getty', 'csh', 'bash',
    'sh', 'powerd', 'thermald', 'mpdecision', 'polkitd', 'whoopsie',
    'mediascanner-service', 'window-stack-bridge', 'dconf-service',
    'pulseaudio', 'hud-service', 'indicator-bluetooth-service',
    'indicator-location-service', 'indicator-sound-service',
    'indicator-secret-agent', 'mtp-server', 'address-book-service',
    'dnsmasq', 'systemd-logind', 'systemd-udevd']

with open(os.path.join(basedir, 'procmapping.txt'), 'w') as mapping:
    procnames = {}
    for p in psutil.process_iter():
        try:
            proc = p.as_dict(attrs=['pid', 'name'])
            if os.getpgid(proc['pid']) != 0:
                procname = os.path.basename(proc['name'])
                fname = os.path.join(
                    default_threshold_path, procname + ".threshold")
                count = procnames.get(procname, 0)
                procnames[procname] = count + 1
                if count > 0:
                    procname = '%s_%d' % (procname, count)
                if not proc['name'] in ignore_procs:
                    if os.path.isfile(fname):
                        mapping.write('%s:%d\n' % (procname, proc['pid']))
                        print(procname)
        except:
            pass
