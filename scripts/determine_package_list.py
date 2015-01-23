#!/usr/bin/env python

# Ubuntu Test Cases for Touch
# Copyright 2015 Canonical Ltd.

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
ADB_SHELL = [os.path.join(HERE, '../utils/host/adb-shell')]


def _adb_shell(command):
    '''Wrapper for adb commands'''
    cmd_args = []
    cmd_args.extend(ADB_SHELL)
    cmd_args.extend(command)
    return subprocess.check_output(cmd_args)


def get_input(in_file_name):
    '''Gets the source package input from the json encoded file'''
    # XXX - fginther 20150120
    # Use a json encoded file instead of a raw text file
    with open(in_file_name) as in_file:
        return in_file.read().splitlines()[0]


def get_binary_package_from_source(source_package):
    '''Return a list of binary packages from the given source package

    Prior to executing this, 'apt-get update' must have been been called on
    the target adb device to acquire the source package data.
    '''
    showsrc = _adb_shell(['apt-cache showsrc {}'.format(source_package)])
    for line in showsrc.splitlines():
        if line.startswith('Binary:'):
            return line[len('Binary: '):].split(', ')
    return []


def get_all_package_list():
    '''Return a list of all packages on the touch device'''
    package_list = []
    packages = _adb_shell(['dpkg --get-selections'])
    for line in packages.splitlines():
        package_name = line.split()[0]
        # XXX - fginther 20150120
        # How do we need to handle architecture specific packages
        # (i.e. 'unity8-private:armhf', 'zlib1g:armhf', etc.)
        # For now, just strip these.
        if ':' in package_name:
            package_name = package_name.split(':')[0]
        package_list.append(package_name)
    return package_list


if __name__ == '__main__':
    source_package = get_input(sys.argv[1])
    all_packages = get_all_package_list()
    binary_packages = get_binary_package_from_source(source_package)
    intersection = set(all_packages) & set(binary_packages)
    print(' '.join(intersection))
    sys.exit(0)
