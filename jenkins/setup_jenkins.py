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

Test = collections.namedtuple('Test', ['name', 'fmt', 'restrict_to'])


def _test(name, fmt='{prefix}{series}-touch_{imagetype}-{type}-'
          'smoke-{testname}', restrict_to=None):
    return Test(name, fmt, restrict_to)


TESTS = [
    _test('install-and-boot'),
    _test('default'),
    _test('mediaplayer-app-autopilot'),
    _test('gallery-app-autopilot'),
    _test('webbrowser-app-autopilot'),
    _test('unity8-autopilot'),
    _test('friends-app-autopilot'),
    _test('notes-app-autopilot'),
    _test('camera-app-autopilot'),
    _test('dialer-app-autopilot'),
    _test('messaging-app-autopilot'),
    _test('address-book-app-autopilot'),
    _test('share-app-autopilot'),
    _test('calendar-app-autopilot'),
    _test('music-app-autopilot'),
    _test('ubuntu-calculator-app-autopilot'),
    _test('ubuntu-clock-app-autopilot'),
    _test('ubuntu-filemanager-app-autopilot'),
    _test('ubuntu-rssreader-app-autopilot'),
    _test('ubuntu-terminal-app-autopilot'),
    _test('ubuntu-weather-app-autopilot'),
    _test('ubuntu-ui-toolkit-autopilot'),
    _test('ubuntu-system-settings-online-accounts-autopilot'),
    _test('click_image_tests'),
    _test('dropping-letters-app-autopilot'),
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


def _configure_job(instance, env, args, config_item, device, test):
    tmpl_name = 'touch-{}.xml.jinja2'.format(test.name)
    params = {
        'host': config_item['node-label'],
        'name': device['name'],
        'publish': args.publish,
        'branch': args.branch,
        'wait': args.wait,
        'imagetype': config_item['image-type'],
    }
    jobname = _get_job_name(args, params['name'], test, params['imagetype'])
    _publish(instance, env, args, tmpl_name, jobname, **params)
    return jobname


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
    jobname = _get_job_name(args, device, _test('master'), image_type)
    _publish(instance, env, args, 'touch-master.xml.jinja2', jobname, **params)


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
            projects = []
            tests = TESTS
            if 'filter' in item:
                tests = item['filter'](tests, _test)
            for test in tests:
                if not test.restrict_to or device in test.restrict_to:
                    logging.debug("configuring %s job for %s",
                                  device['name'], test.name)
                    p = _configure_job(
                        jenkins_inst, env, args, item, device, test)
                    projects.append(p)
                else:
                    logging.info('%s not configured for %s',
                                 device['name'], test.name)
            _configure_master(jenkins_inst, env, args, projects, item, device)

if __name__ == '__main__':
    main()
