#!/usr/bin/python

import datetime
import sys

from xml.etree import ElementTree

import yaml


def _convert_testcase(tc):
    x = {
        'testcase': tc.attrib['name'],
        'testsuite': tc.attrib['classname'],
        'command': 'autopilot',
        'cmd_type': 'testcase_test',
        'stdout': '',
        'stderr': '',
        'returncode': 0
    }
    t = tc.attrib.get('time', False)
    if t:
        x['time_delta'] = t

    for e in tc.getchildren():
        if e.tag in ('failure', 'error'):
            x['stderr'] = e.text
            x['returncode'] = 1
        elif e.tag == 'skip':
            # NOTE: this isn't a real thing in UTAH. However, the
            # qa-dashboard code doesn't care and will display it as skipped
            x['cmd_type'] = 'testcase_skipped'
            x['stdout'] = e.text
        else:
            raise RuntimeError('Unknown element type: %s' % e.tag)
    return x


def _get_results(stream):
    tree = ElementTree.fromstring(stream.read())
    results = {
        'errors': int(tree.attrib.get('errors', '0')),
        'failures': int(tree.attrib.get('failures', '0')),
        'commands': [],
        'fetch_errors': 0,
        'uname': 'n/a',
        'media-info': 'n/a',
        'install_type': 'n/a',
        'arch': 'n/a',
        'release': 'n/a',
        'build_number': 'n/a',
        'name': 'unamed',
        'runlist': 'n/a',
        'ran_at': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
    }
    results['passes'] = \
        int(tree.attrib['tests']) - results['errors'] - results['failures']

    for tc in tree.getchildren():
        results['commands'].append(_convert_testcase(tc))
    return results


def _main(stream):
    results = _get_results(stream)
    print(yaml.safe_dump(results, default_flow_style=False))


if __name__ == '__main__':
    exit(_main(sys.stdin))
