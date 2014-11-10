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

import os
import mock
import unittest
import sys
import time

path = os.path.join(os.path.dirname(__file__), '../scripts')
sys.path.append(path)

import statsd


class TestStatsd(unittest.TestCase):

    def setUp(self):
        self.origkey = os.environ.get('STATSD_KEY')
        os.environ['STATSD_KEY'] = 'prefix'
        reload(statsd)

    def tearDown(self):
        if not self.origkey:
            del os.environ['STATSD_KEY']
        else:
            os.environ['STATSD_KEY'] = self.origkey
        reload(statsd)

    """Simple set of tests to make sure the statsd calls work."""

    @mock.patch('txstatsd.metrics.metric.Metric.write')
    def testGaugeIt(self, _statsd):
        statsd.gauge_it('foo', None)
        _statsd.assert_called_with('prefix.foo:0|g')
        _statsd.reset_mock()

        statsd.gauge_it('foo', [])
        _statsd.assert_called_with('prefix.foo:0|g')
        _statsd.reset_mock()

        statsd.gauge_it('foo', [1, 2, 3])
        _statsd.assert_called_with('prefix.foo:3|g')
        _statsd.reset_mock()

    @mock.patch('txstatsd.metrics.metric.Metric.write')
    def testTimeIt(self, _statsd):
        with statsd.time_it('foo'):
            time.sleep(0.1)
        # should have a timing of about 100ms
        self.assertRegexpMatches(
            _statsd.call_args[0][0], 'prefix.foo:100.[\d+]|ms')
