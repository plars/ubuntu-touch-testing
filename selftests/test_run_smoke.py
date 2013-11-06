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

import imp
import mock
import os
import subprocess
import unittest


class TestRunSmoke(unittest.TestCase):

    """Simple set of tests to make sure the smoke-run command works."""

    def setUp(self):
        # load the module
        module = 'run-smoke'
        fname = os.path.join(os.path.dirname(__file__), '../scripts', module)
        self.run_smoke = imp.load_source(module, fname)
        if 'ANDROID_SERIAL' in os.environ:
            del os.environ['ANDROID_SERIAL']

    @mock.patch.dict('os.environ')
    @mock.patch('subprocess.check_output')
    def testSerialRequired(self, check_output):
        '''Ensure android serial is required when appropriate'''
        check_output.return_value = '1'.encode()
        self.assertTrue(self.run_smoke._serial_required())

        check_output.return_value = '1\n2\n3\n4'.encode()
        self.assertFalse(self.run_smoke._serial_required())

        check_output.return_value = '1\n2\n3\n4\n5'.encode()
        self.assertTrue(self.run_smoke._serial_required())

        # make sure serial isn't required if specified in env
        os.environ['ANDROID_SERIAL'] = 'foo'
        check_output.return_value = '1\n2\n3\n4\n5'.encode()
        self.assertFalse(self.run_smoke._serial_required())

    @mock.patch('statsd.gauge_it')
    def testAssertArgs(self, gauge):
        '''Ensure install-url is used properly'''
        patterns = [
            (['--install-url', 'x', '-p', 'x'], False),
            (['--install-url', 'x', '-P', 'x'], False),
            (['--install-url', 'x', '--image-opt', 'x'], False),
            (['-p', 'x', '-P', 'x', '--image-opt', 'x'], True),
        ]
        for pat, val in patterns:
            args = self.run_smoke._get_parser().parse_args(['-s', 'foo'] + pat)
            self.assertEqual(val, self.run_smoke._assert_args(args))

        # ensure the -p ALL pulls in all packages
        gauge.reset_mock()
        args = self.run_smoke._get_parser().parse_args(['-p', 'ALL'])
        self.assertTrue(self.run_smoke._assert_args(args))
        self.assertTrue(len(args.package) > 1)
        args = gauge.call_args_list[0][0]
        self.assertEqual('PACKAGES', args[0])
        self.assertLess(1, len(args[1]))

        args = gauge.call_args_list[1][0]
        self.assertEqual('APPS', args[0])
        self.assertIsNone(args[1])
        args = gauge.call_args_list[2][0]
        self.assertEqual('TESTS', args[0])
        self.assertIsNone(args[1])

        # don't bother checking gauge calls for the remaining "ALL" tests

        # ensure the -a ALL pulls in all APPS
        args = self.run_smoke._get_parser().parse_args(['-a', 'ALL'])
        self.assertTrue(self.run_smoke._assert_args(args))
        self.assertTrue(len(args.app) > 1)

        # ensure the -t ALL pulls in all TESTS
        args = self.run_smoke._get_parser().parse_args(['-t', 'ALL'])
        self.assertTrue(self.run_smoke._assert_args(args))
        self.assertTrue(len(args.test) > 1)

    def testAssertArgsEnv(self):
        '''Ensure we pull in environment variables that jenkins uses.'''
        with mock.patch.dict('os.environ'):
            os.environ['APPS'] = 'apps'
            os.environ['TESTS'] = 'tests'
            os.environ['PACKAGES'] = 'packages'
            os.environ['PPAS'] = 'ppas'
            os.environ['IMAGE_TYPE'] = 'type'
            os.environ['INSTALL_URL'] = 'url'
            os.environ['IMAGE_OPT'] = 'opts opts'
            os.environ['ANDROID_SERIAL'] = 'foo'

            args = self.run_smoke._get_parser().parse_args([])
            self.assertTrue(self.run_smoke._assert_args(args))

            self.assertEqual(args.app, ['apps'])
            self.assertEqual(args.test, ['tests'])
            self.assertEqual(args.package, ['packages'])
            self.assertEqual(args.ppa, ['ppas'])
            self.assertEqual(args.image_type, 'type')
            self.assertEqual(args.install_url, 'url')
            self.assertEqual(args.image_opt, 'opts opts')

    def testProvision(self):
        orig = os.environ.get('IMAGE_OPT', '')
        with mock.patch.object(self.run_smoke, '_run') as run:
            args = self.run_smoke._get_parser().parse_args(
                ['-s', 'foo', '--image-opt', 'FOOBAR', '-p', '1', '-p', '2'])
            self.run_smoke._provision(args)
            self.assertTrue(run.called)
            val = os.environ.get('IMAGE_OPT')
            os.environ['IMAGE_OPT'] = orig
            self.assertEqual('FOOBAR', val)

    def testUtahTests(self):
        args = self.run_smoke._get_parser().parse_args(
            ['-s', 'foo', '-t', 'a', '-t', 'b'])
        with mock.patch.object(self.run_smoke, '_run') as run:
            with mock.patch.dict('os.environ'):
                run.side_effects = [subprocess.CalledProcessError, None]
                self.run_smoke._test_utah(args)
                p = os.path.join(self.run_smoke.res_dir, 'b')
                # ensuring b ran means, that we handled the failure of test
                # 'a' and that the environment is setup correctly
                self.assertEqual(os.environ['RESDIR'], p)
