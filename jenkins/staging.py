# The configuration matrix of our staging device testing

import os

if not os.environ.get('MEGA', False):
    raise RuntimeError('staging server only supports MEGA jobs')

JENKINS = 'http://jenkins-dev-image-test:8080/'

MATRIX = [
    {
        'image-type': 'touch_mir',
        'node-label': 'ashes',
        'devices': [
            {'name': 'mako-06 || mako-07 || mako-08'},
        ],
    },
]
