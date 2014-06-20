#!/usr/bin/python3
#
#
# Copyright (C) 2013 Canonical
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
#
#
# Syntax:
# 	health-check-test-pid.py pid [ path-to-threshold-files ]
#
# The process name is resolved and the tool will use a
# `procname`.threshold file to compare against.  If this file does not exist,
# default.threshold is used.
#

import json
import os
import subprocess
import sys
import psutil
import platform

#
# Default test run durations in seconds
#
default_duration = 60

default_threshold_path = os.path.join(
    os.path.join(os.path.dirname(__file__), 'thresholds'), platform.machine())

default_pass_unknown_process = True


def read_threshold(procname):
    """Parse thresholds file.

    lines starting with '#' are comments
    format is: key value, e.g.
       health-check.cpu-load.cpu-load-total.total-cpu-percent  0.5
       health-check.cpu-load.cpu-load-total.user-cpu-percent   0.5
       health-check.cpu-load.cpu-load-total.system-cpu-percent 0.5
    """
    fname = default_threshold_path + "/" + procname + ".threshold"
    thresholds = {}
    n = 0

    with open(fname) as file:
        for line in file:
            n = n + 1
            if len(line) > 1 and not line.startswith("#"):
                tmp = line.split()
                if len(tmp) == 2:
                    thresholds[tmp[0]] = tmp[1]
                else:
                    sys.stderr.write(
                        "Threshold file %s line %d format error" % (fname, n))

    return thresholds


def check_threshold(data, key, fullkey, threshold):
    """Locate a threshold in the JSON data, compare it to the threshold"""

    try:
        d = data[key[0]]
    except KeyError:
        sys.stderr.write(
            "health-check JSON data does not have key " + fullkey + "\n")
        return (True, "Attribute not found and ignored")

    key = key[1:]
    if len(key) > 0:
        return check_threshold(d, key, fullkey, threshold)
    else:
        val = float(d)
        if threshold >= val:
            cmp = str(threshold) + " >= " + str(val)
            return (True, cmp)
        else:
            cmp = str(threshold) + " < " + str(val)
            return (False, cmp)


def check_thresholds(procname, data, thresholds):
    print("process: " + procname)
    failed = False
    for key in sorted(thresholds.keys()):
        if key.startswith("health-check"):
            threshold = float(thresholds[key])
            (ret, str) = check_threshold(data, key.split('.'), key, threshold)
            if ret:
                msg = "PASSED"
            else:
                msg = "FAILED"
                failed = True

            sys.stderr.write(msg + ": " + str + ": " + key + "\n")

    return failed


def health_check(pid, procname):
    """run health-check on a given process

    :return: True if failed, False if passed
    """
    thresholds = read_threshold(procname)
    #
    #  Can't test without thresholds
    #
    if len(thresholds) == 0:
        if default_pass_unknown_process:
            sys.stderr.write("No thresholds for process " + procname + "\n")
            sys.stderr.write("Defaulting to pass this test\n")
            return False
        else:
            thresholds = read_threshold("default")
            if len(thresholds) == 0:
                sys.stderr.write(
                    "No thresholds for process " + procname + "\n")
            else:
                sys.stderr.write(
                    "Using default thresholds for process " + procname + "\n")

    duration = default_duration

    if 'duration' in thresholds:
        duration = int(thresholds['duration'])

    filename = "health-check-" + str(pid) + ".json"
    args = [
        'health-check', '-c', '-f', '-d', str(duration),
        '-w', '-W', '-r', '-p', str(pid), '-o', filename
    ]

    try:
        subprocess.check_output(args)
        with open(filename) as f:
            data = json.load(f)
            return check_thresholds(procname, data, thresholds)
    except subprocess.CalledProcessError as e:
        print(e)
        exit(1)


def get_proc(pid):
    proc = None
    try:
        p = psutil.Process(pid)
        pgid = os.getpgid(pid)
        if pgid == 0:
            sys.stderr.write(
                "Cannot run health-check on kernel task with PID(%d)\n" % pid)
        else:
            proc = p
    except psutil.NoSuchProcess as e:
        sys.stderr.write('%s\n' % e)
    except OSError as e:
        if e.errno == 3:
            sys.stderr.write("Cannot find pgid on process with PID %d\n" % pid)
    return proc


def main(pid):
    if os.getuid() != 0:
        sys.stderr.write("Need to run as root\n")
        exit(1)

    p = get_proc(pid)
    if not p:
        exit(1)

    procname = os.path.basename(p.name)
    if (health_check(pid, procname)):
        exit(1)
    else:
        exit(0)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s PID\n" % sys.argv[0])
        exit(1)

    pid = int(sys.argv[1])
    main(pid)
