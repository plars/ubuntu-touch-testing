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

from mock import patch
import unittest

from determine_package_list import (
    get_binary_package_from_source,
    get_all_package_list,
)


class TestBoottest(unittest.TestCase):
    pass


class TestDeterminePackageList(unittest.TestCase):
    @patch('determine_package_list._adb_shell')
    def test_get_single_binary_from_source(self, adb):
        adb.return_value = 'Binary: foo'
        actual = get_binary_package_from_source('foo_source')
        self.assertEqual(['foo'], actual)

    @patch('determine_package_list._adb_shell')
    def test_get_many_binaries_from_source(self, adb):
        adb.return_value = 'Binary: foo, bar, baz'
        actual = get_binary_package_from_source('foo_source')
        self.assertEqual(['foo', 'bar', 'baz'], actual)

    @patch('determine_package_list._adb_shell')
    def test_get_no_binaries_from_source(self, adb):
        adb.return_value = ''
        actual = get_binary_package_from_source('foo_source')
        self.assertEqual([], actual)


class TestGetAllPackageList(unittest.TestCase):
    @patch('determine_package_list._adb_shell')
    def test_get_all_packages(self, adb):
        adb.return_value = '\n'.join([
            'package1\t1.2.3',
            'package2:armhf 2.3.4',
            'package3       3.4.5',
        ])
        actual = get_all_package_list()
        self.assertEqual(['package1', 'package2', 'package3'], actual)

    @patch('determine_package_list._adb_shell')
    def test_get_all_packages_no_packages(self, adb):
        adb.return_value = ''
        actual = get_all_package_list()
        self.assertEqual([], actual)

if __name__ == '__main__':
    unittest.main()
