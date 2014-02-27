# The configuration matrix of our production device testing

JENKINS = 'http://q-jenkins:8080'


def _url(channel, device):
    return 'http://system-image.ubuntu.com/%s/%s/index.json' \
           % (channel, device)


TRUSTY_MATRIX = [
    {
        'image-type': 'touch_sf4p',
        'include-qa': False,
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
                'name': 'maguro',
                'slave-label': 'daily-maguro',
                'trigger_url': _url('trusty-proposed', 'maguro'),
            },
        ],
    },
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
            {
                'name': 'maguro',
                'slave-label': 'daily-maguro',
                'trigger_url': _url('trusty-proposed', 'maguro'),
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
        'IMAGE_OPT': 'export IMAGE_OPT="ubuntu-system -b '
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
            {
                'name': 'maguro',
                'slave-label': 'daily-maguro',
                'trigger_url': _url('saucy-proposed', 'maguro'),
            },
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="ubuntu-system -b '
                     '--channel saucy-proposed"'
    },
]

MATRIX = {
    'trusty': TRUSTY_MATRIX,
    'saucy': SAUCY_MATRIX,
}
