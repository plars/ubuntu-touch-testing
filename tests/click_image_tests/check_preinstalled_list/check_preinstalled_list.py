#!/usr/bin/python3
# Copyright (C) 2013 Canonical Ltd.
# Author: Sergio Schvezov <sergio.schvezov@canonical.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import unittest
import urllib.request


click_list_url = \
    'http://people.canonical.com/~ubuntu-archive/click_packages/click_list'


def get_install_list():
    request = urllib.request.urlopen(click_list_url).read().decode('utf-8')
    click_files = [x for x in request.split('\n') if x]
    click_apps = {}
    for entry in click_files:
        entry_parts = entry.split('_')
        click_apps[entry_parts[0]] = entry_parts[1]
    return click_apps


def get_image_list():
    click_list = subprocess.check_output(
        ['adb', 'shell', 'sudo', '-u', 'phablet',
         'bash', '-ic', 'click list']).decode('utf-8').split('\n')
    click_entries = [x for x in click_list if x]
    click_apps = {}
    for entry in click_entries:
        entry_parts = entry.split('\t')
        click_apps[entry_parts[0]] = entry_parts[1].strip()
    return click_apps


class ClickPreinstalled(unittest.TestCase):

    def setUp(self):
        self.image_list = get_image_list()
        self.install_list = get_install_list()
        print('Search for %s on image' % self.install_list.keys())

    def testPreinstalled(self):
        for entry in self.install_list:
            self.assertIn(entry, self.image_list.keys())


if __name__ == '__main__':
    unittest.main()
