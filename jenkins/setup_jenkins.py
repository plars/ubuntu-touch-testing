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
import jenkins
import jinja2
import logging
import os

from distro_info import UbuntuDistroInfo
DEV_SERIES = UbuntuDistroInfo().devel()


SYSTEM_IMAGE = os.environ.get('SYSTEM_IMAGE', False)

Test = collections.namedtuple('Test', ['name', 'fmt', 'restrict_to'])


if SYSTEM_IMAGE:
    def _test(name, fmt='{prefix}{series}-touch_ro-{type}-smoke-{testname}',
              restrict_to=None):
        return Test(name, fmt, restrict_to)
else:
    def _test(name, fmt='{prefix}{series}-touch-{type}-smoke-{testname}',
              restrict_to=None):
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
    _test('phone-app-connected-autopilot', restrict_to=['maguro-02']),
    _test('share-app-autopilot'),
    _test('calendar-app-autopilot'),
    _test('music-app-autopilot'),
    _test('ubuntu-calculator-app-autopilot'),
    _test('ubuntu-clock-app-autopilot'),
    #_test('ubuntu-docviewer-app-autopilot'),
    _test('ubuntu-filemanager-app-autopilot'),
    _test('ubuntu-rssreader-app-autopilot'),
    _test('ubuntu-terminal-app-autopilot'),
    _test('ubuntu-weather-app-autopilot'),
    _test('sdk'),
    _test('security'),
]

DEVICES = [
    "mako-01",
    "maguro-01",
    "manta-01",
    "grouper-02",
]


if SYSTEM_IMAGE:
    #TESTS = [_test('upgrade')] + TESTS
    TESTS += [
        _test('smem',
              '{prefix}{testname}-{series}-'
              'touch_ro-armhf-install-idle-{type}'),
        _test('memevent',
              '{prefix}{testname}-{series}-touch_ro-armhf-default-{type}'),
    ]
    DEVICES = ['mako-05', 'maguro-02']
else:
    TESTS += [
        _test('smem',
              '{prefix}{testname}-{series}-touch-armhf-install-idle-{type}'),
        _test('memevent',
              '{prefix}{testname}-{series}-touch-armhf-default-{type}'),
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
    parser.add_argument("-P", "--publish", action="store_true",
                        help="Publish at the end of the job")
    parser.add_argument("-p", "--password",
                        help="username to use when logging into Jenkins")
    parser.add_argument("--prefix",
                        help="Prefix to add to the beginning of the job name")
    parser.add_argument("-j", "--jenkins", default="http://10.98.0.1:8080/",
                        help="URL of jenkins instance to configure jobs in.")
    parser.add_argument("-n", "--name", action='append',
                        help=("Device names where the job should be executed."
                              " Can be used more than once."))
    parser.add_argument("-s", "--series", default=DEV_SERIES,
                        help=("series of Ubuntu to download "
                              "(default=%(default)s)"))
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


def _get_job_name(args, device, test):
    prefix = ""
    if(args.prefix):
        prefix = args.prefix + "-"
    return test.fmt.format(prefix=prefix,
                           series=args.series,
                           testname=test.name,
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


def _configure_job(instance, env, args, device, test):
    tmpl_name = 'touch-{}.xml.jinja2'.format(test.name)
    params = {
        'name': device,
        'publish': args.publish
    }
    params['system_image'] = True if SYSTEM_IMAGE else False
    jobname = _get_job_name(args, device, test)
    _publish(instance, env, args, tmpl_name, jobname, **params)


def _configure_master(instance, env, args, device, projects):
    device_type = device[:device.index("-")]
    trigger_url = ('http://cdimage.ubuntu.com/ubuntu-touch/daily-preinstalled/'
                   'pending/MD5SUMS')
    if SYSTEM_IMAGE:
        fmt = 'http://system-image.ubuntu.com/daily/{}/index.json'
        trigger_url = fmt.format(device_type)

    params = {
        'name': device,
        'publish': args.publish,
        'projects': projects,
        'trigger_url': trigger_url
    }
    jobname = _get_job_name(args, device, _test('master'))
    _publish(instance, env, args, 'touch-master.xml.jinja2', jobname, **params)


def _dryrun_func(jobname, config):
    logging.debug(jobname)
    logging.debug(config)


def main():
    logging.basicConfig(level=logging.DEBUG)
    args = _get_parser().parse_args()

    jenkins_inst = _get_jenkins(args.jenkins, args.username, args.password)
    if args.dryrun:
        jenkins_inst.create_job = _dryrun_func
        jenkins_inst.reconfig_job = _dryrun_func

    env = _get_environment()

    device_list = args.name if args.name else DEVICES

    for device in device_list:
        projects = []
        for test in TESTS:
            logging.debug("configuring job for %s", test.name)
            if not test.restrict_to or device in test.restrict_to:
                _configure_job(jenkins_inst, env, args, device, test)
                projects.append(_get_job_name(args, device, test))
            else:
                logging.info('%s not configured for %s', device, test.name)

        _configure_master(jenkins_inst, env, args, device, projects)

if __name__ == '__main__':
    main()
