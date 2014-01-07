# The configuration matrix of our staging device testing

import os

if not os.environ.get('MEGA', False):
    raise RuntimeError('staging server only supports MEGA jobs')

JENKINS = 'http://dev-jenkins.ubuntu-ci:8080/'

TRUSTY_MATRIX = [
    {
        'image-type': 'touch',
        'node-label': 'touch-dev',
        'statsd-key': 'ubuntu-ci.test-execution-service.staging',
        'dashboard-host': '162.213.34.3',
        'dashboard-user': 'doanac',
        'dashboard-prefix': '/staging',
        'devices': [
            {
                'name': 'mako',
                'trigger_url': 'http://system-image.ubuntu.com/trusty-proposed/mako/index.json'
            }
        ],
    },
]

MATRIX = {
    'trusty': TRUSTY_MATRIX,
}
