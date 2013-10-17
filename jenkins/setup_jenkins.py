#!/usr/bin/env python

# Ubuntu Testing Automation Harness
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

import argparse
import collections
import imp
import jenkins
import jinja2
import logging
import os

from distro_info import UbuntuDistroInfo
DEV_SERIES = UbuntuDistroInfo().devel()

DEFINE_MEGA = os.environ.get('MEGA', False)

DEF_FMT = '{prefix}{series}-touch_{imagetype}-{type}-smoke-{testname}'

Test = collections.namedtuple('Test', ['name', 'fmt', 'ap', 'pkgs'])


def _test(name, fmt=DEF_FMT):
    return Test(name, fmt, None, None)


def _ap_test(name, fmt=DEF_FMT, packages=None):
    # convert share-app-autopilot to share_app
    ap = name.replace('-', '_').replace('_autopilot', '')
    if packages is None:
        packages = [name]
    return Test(name, fmt, ap, packages)


TESTS = [
    _test('install-and-boot'),
    _test('default'),
    _ap_test('mediaplayer-app-autopilot'),
    _ap_test('gallery-app-autopilot'),
    _ap_test('webbrowser-app-autopilot'),
    _ap_test('unity8-autopilot', packages=[]),
    _ap_test('friends-app-autopilot'),
    _ap_test('notes-app-autopilot', packages=[]),
    _ap_test('camera-app-autopilot'),
    _ap_test('dialer-app-autopilot'),
    _ap_test('messaging-app-autopilot'),
    _ap_test('address-book-app-autopilot'),
    _ap_test('share-app-autopilot'),
    _ap_test('calendar-app-autopilot', packages=['python-dateutil']),
    _ap_test('music-app-autopilot', packages=[]),
    _ap_test('ubuntu-calculator-app-autopilot', packages=[]),
    _ap_test('ubuntu-clock-app-autopilot', packages=[]),
    _ap_test('ubuntu-filemanager-app-autopilot', packages=[]),
    _ap_test('ubuntu-rssreader-app-autopilot', packages=[]),
    _ap_test('ubuntu-terminal-app-autopilot', packages=[]),
    _ap_test('ubuntu-weather-app-autopilot', packages=[]),
    _ap_test('ubuntu-ui-toolkit-autopilot'),
    _ap_test('ubuntu-system-settings-online-accounts-autopilot'),
    _test('click_image_tests'),
    _ap_test('dropping-letters-app-autopilot', packages=[]),
    _test('sdk'),
    _test('security'),
    _test('eventstat',
          '{prefix}{testname}-{series}-touch_{imagetype}-armhf-install-idle-{type}'),
    _test('smem',
          '{prefix}{testname}-{series}-touch_{imagetype}-armhf-install-idle-{type}'),
    _test('memevent',
          '{prefix}{testname}-{series}-touch_{imagetype}-armhf-default-{type}'),
]


def _get_parser():
    """Create and return command line parser.

    :returns: command line parser
    :rtype: argparse.ArgumentParser

    """
    parser = argparse.ArgumentParser(
        description='Create/Update upgrade testing jenkins jobs.')
    parser.add_argument("-d", "--dryrun", action="store_true",
                        help="Dry run mode. Don't execute jenkins commands.")
    parser.add_argument("-u", "--username",
                        help="username to use when logging into Jenkins.")
    parser.add_argument("-p", "--password",
                        help="username to use when logging into Jenkins")
    parser.add_argument("-b", "--branch", default="lp:ubuntu-test-cases/touch",
                        help="The branch this is located. default=%(default)s")
    parser.add_argument("-c", "--config", required=True,
                        type=argparse.FileType('r'),
                        help="The job config to use.")
    parser.add_argument("-P", "--publish", action="store_true",
                        help="Publish at the end of the job")
    parser.add_argument("--prefix",
                        help="Prefix to add to the beginning of the job name")
    parser.add_argument("-s", "--series", default=DEV_SERIES,
                        help=("series of Ubuntu to download "
                              "(default=%(default)s)"))
    parser.add_argument("-w", "--wait", type=int, default=300,
                        help=("How long to wait after jenkins triggers the"
                              "install-and-boot job (default=%(default)d)"))
    return parser


def _get_jenkins(url, username, password):
    logging.info('Attempting to login to jenkins at %s', url)
    if username is not None:
        logging.info('...with authentication as user: %s', username)
        instance = jenkins.Jenkins(url, username=username, password=password)
    else:
        logging.info('...without authentication')
        instance = jenkins.Jenkins(url)

    return instance


def _get_environment():
    base = os.path.join(os.path.dirname(__file__), 'templates')
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(base),
        undefined=jinja2.StrictUndefined,
        trim_blocks=True)


def _get_job_name(args, device, test, image_type):
    prefix = ""
    if(args.prefix):
        prefix = args.prefix + "-"
    return test.fmt.format(prefix=prefix,
                           series=args.series,
                           testname=test.name,
                           imagetype=image_type,
                           type=device[:device.index("-")])


def _publish(instance, env, args, template, jobname, **params):
    tmpl = env.get_template(template)
    cfg = tmpl.render(**params)
    if args.dryrun:
        _dryrun_func(jobname, cfg)
        return
    if instance.job_exists(jobname):
        logging.info('reconfiguring job %s', jobname)
        instance.reconfig_job(jobname, cfg)
    else:
        logging.info('creating job %s', jobname)
        instance.create_job(jobname, cfg)


if DEFINE_MEGA:
    def _configure_jobs(instance, env, args, config_item, device, tests):
        name = device['name']
        device_type = name[:name.index("-")]
        defserial = '$(${BZRDIR}/scripts/get-adb-id ${NODE_NAME})'
        fmt = 'http://system-image.ubuntu.com/devel-proposed/{}/index.json'
        trigger_url = fmt.format(device_type)

        packages = []
        ap_tests = []
        ut_tests = []

        for test in tests:
            if test.ap:
                ap_tests.append(test.ap)
                if test.pkgs is not None:
                    packages.extend(test.pkgs)
            else:
                ut_tests.append(test.name)

        params = {
            'name': name,
            'serial': device.get('serial', defserial),
            'publish': args.publish,
            'branch': args.branch,
            'tests': ' '.join(ut_tests),
            'ap_tests': ' '.join(ap_tests),
            'packages': ' '.join(packages),
            'trigger_url': trigger_url,
            'wait': args.wait,
            'imagetype': config_item['image-type'],
            'image_opt': config_item.get('IMAGE_OPT', ''),
        }
        # a hack so we can use _get_job_name
        test = _test('', fmt='{prefix}{series}-touch_{imagetype}-{type}')
        job = _get_job_name(args, name, test, config_item['image-type'])
        _publish(instance, env, args, 'touch-smoke.xml.jinja2', job, **params)
else:
    def _configure_job(instance, env, args, config_item, device, test):
        tmpl_name = 'touch-{}.xml.jinja2'.format(test.name)
        defserial = '$(${BZRDIR}/scripts/get-adb-id %s)' % device['name']
        params = {
            'host': config_item['node-label'],
            'name': device['name'],
            'serial': device.get('serial', defserial),
            'publish': args.publish,
            'branch': args.branch,
            'wait': args.wait,
            'imagetype': config_item['image-type'],
            'image_opt': config_item.get('IMAGE_OPT', ''),
        }
        job = _get_job_name(args, params['name'], test, params['imagetype'])
        _publish(instance, env, args, tmpl_name, job, **params)
        return job

    def _configure_master(instance, env, args, projects, config_item, device):
        device = device['name']
        device_type = device[:device.index("-")]
        fmt = 'http://system-image.ubuntu.com/devel-proposed/{}/index.json'
        trigger_url = fmt.format(device_type)

        params = {
            'host': config_item['node-label'],
            'name': device,
            'publish': args.publish,
            'branch': args.branch,
            'projects': projects,
            'trigger_url': trigger_url
        }
        image_type = config_item['image-type']
        job = _get_job_name(args, device, _test('master'), image_type)
        _publish(instance, env, args, 'touch-master.xml.jinja2', job, **params)

    def _configure_jobs(instance, env, args, config_item, device, tests):
        projects = []
        for test in tests:
            logging.debug("configuring %s job for %s",
                          device['name'], test.name)
            p = _configure_job(instance, env, args, config_item, device, test)
            projects.append(p)
        _configure_master(instance, env, args, projects, config_item, device)


def _dryrun_func(jobname, config):
    logging.debug(jobname)
    logging.debug(config)


def main():
    logging.basicConfig(level=logging.DEBUG)
    args = _get_parser().parse_args()

    config = imp.load_source('', 'config.py', args.config)

    jenkins_inst = _get_jenkins(config.JENKINS, args.username, args.password)
    if args.dryrun:
        jenkins_inst.create_job = _dryrun_func
        jenkins_inst.reconfig_job = _dryrun_func

    env = _get_environment()

    for item in config.MATRIX:
        for device in item['devices']:
            tests = TESTS
            if 'filter' in item:
                tests = item['filter'](tests, _test)
            _configure_jobs(jenkins_inst, env, args, item, device, tests)

if __name__ == '__main__':
    main()
