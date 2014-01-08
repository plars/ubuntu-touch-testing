# The configuration matrix of our staging device testing

JENKINS = 'http://dev-jenkins.ubuntu-ci:8080/'

TRUSTY_MATRIX = [
    {
        'image-type': 'touch',
        'statsd-key': 'ubuntu-ci.daily-image.staging',
        'dashboard-host': '162.213.34.3',
        'dashboard-user': 'doanac',
        'dashboard-prefix': '/staging',
        'devices': [
            {
                'name': 'mako',
                'slave-label': 'test_execution_service-mako',
                'trigger_url': 'http://system-image.ubuntu.com/trusty-proposed/mako/index.json'
            }
        ],
    },
]

MATRIX = {
    'trusty': TRUSTY_MATRIX,
}
