#!/usr/bin/env python

import subprocess
import sys

def get_input(in_file_name):
    '''Gets the source package input from the json encoded file'''
    # XXX - fginther 20150120
    # Use a json encoded file instead of a raw text file
    with open(in_file_name) as in_file:
        return in_file.read().splitlines()[0]


def get_binary_package_from_source(source_package):
    '''Return a list of binary packages from the given source package.'''
    subprocess.check_output(['adb', 'shell', 'apt-get update'])
    showsrc = subprocess.check_output(
        ['adb', 'shell', 'apt-cache showsrc {}'.format(source_package)])
    for line in showsrc.splitlines():
        if line.startswith('Binary:'):
            return line[len('Binary: '):].split(', ')


def get_all_package_list():
    '''Return a list of all packages on the touch device'''
    package_list = []
    packages = subprocess.check_output(
        ['adb', 'shell', 'dpkg --get-selections'])
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
