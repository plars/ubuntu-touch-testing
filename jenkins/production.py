# The configuration matrix of our production device testing

JENKINS = 'http://q-jenkins.ubuntu-ci:8080'


def _url(channel, device):
    return 'http://system-image.ubuntu.com/ubuntu-touch/%s/%s/index.json' \
           % (channel, device)


TRUSTY_MATRIX = [
    {
        'image-type': 'touch',
        'include-qa': True,
        'dashboard-host': 'ci.ubuntu.com',
        'dashboard-port': '80',
        'dashboard-user': 'doanac',
        'devices': [
            {
                'name': 'mako',
                'slave-label': 'daily-mako',
                'trigger_url': _url('trusty-proposed', 'mako'),
            },
            {
                'name': 'flo',
                'slave-label': 'daily-flo',
                'trigger_url': _url('trusty-proposed', 'flo'),
            },
            {
                'name': 'manta',
                'slave-label': 'daily-manta',
                'trigger_url': _url('trusty-proposed', 'manta'),
            },
        ],
    },
    {
        'image-type': 'touch_custom',
        'include-qa': False,
        'dashboard-host': 'ci.ubuntu.com',
        'dashboard-port': '80',
        'dashboard-user': 'doanac',
        'devices': [
            {
                'name': 'mako',
                'slave-label': 'daily-mako',
                'trigger_url': _url('trusty-proposed-customized', 'mako'),
            },
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="--bootstrap '
                     '--channel trusty-proposed-customized"'
    },
]

SAUCY_MATRIX = [
    {
        'image-type': 'touch_mir',
        'include-qa': True,
        'dashboard-host': 'ci.ubuntu.com',
        'dashboard-port': '80',
        'dashboard-user': 'doanac',
        'devices': [
            {
                'name': 'mako',
                'slave-label': 'daily-mako',
                'trigger_url': _url('saucy-proposed', 'mako'),
            },
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="--bootstrap '
                     '--channel saucy-proposed"'
    },
]

MATRIX = {
    'trusty': TRUSTY_MATRIX,
    'saucy': SAUCY_MATRIX,
}
