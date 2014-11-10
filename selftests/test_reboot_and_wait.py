# Ubuntu Test Cases for Touch
# Copyright 2013 Canonical Ltd.

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import imp
import mock
import os
import unittest


class TestRebootAndWait(unittest.TestCase):

    """Simple set of tests to make sure the reboot-and-wait command works."""

    def setUp(self):
        # do some trickery to load this as module
        module = 'reboot-and-wait'
        fname = os.path.join(os.path.dirname(__file__), '../scripts', module)
        m = imp.load_source(module, fname)
        self._main = m.main
        self._get_parser = m._get_arg_parser

    @mock.patch('phabletutils.device.AndroidBridge.reboot')
    def testRebootFail(self, reboot):
        reboot.side_effect = RuntimeError('foo')
        args = self._get_parser().parse_args([])
        with self.assertRaisesRegexp(RuntimeError, 'foo'):
            self._main(args)

    @mock.patch('phabletutils.device.AndroidBridge.reboot')
    @mock.patch('phabletutils.device.AndroidBridge.wait_for_device')
    def testWaitForDeviceFail(self, wait_for, reboot):
        wait_for.side_effect = RuntimeError('foo')
        args = self._get_parser().parse_args([])
        with self.assertRaisesRegexp(RuntimeError, 'foo'):
            self._main(args)
        reboot.assert_called_once_with()

    @mock.patch('phabletutils.device.AndroidBridge.reboot')
    @mock.patch('phabletutils.device.AndroidBridge.wait_for_device')
    @mock.patch('phabletutils.device.AndroidBridge.wait_for_network')
    def testRetries(self, wait_for_net, wait_for_dev, reboot):
        args = self._get_parser().parse_args([])
        wait_for_net.side_effect = RuntimeError('foo')
        self.assertEquals(1, self._main(args))
        self.assertEquals(args.num_tries, reboot.call_count)

        # now make sure it can recover after a single network failure
        reboot.reset_mock()
        wait_for_net.reset_mock()
        wait_for_net.side_effect = [RuntimeError('foo'), None]
        self.assertEquals(0, self._main(args))
        self.assertEquals(2, reboot.call_count)
