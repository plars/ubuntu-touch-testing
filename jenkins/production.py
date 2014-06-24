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
        'IMAGE_OPT': 'export IMAGE_OPT="--bootstrap '
                     '--channel trusty-proposed"'
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


UTOPIC_MATRIX = [
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
                'trigger_url': _url('utopic-proposed', 'mako'),
                'num-workers': 3,
            },
            {
                'name': 'flo',
                'slave-label': 'daily-flo',
                'trigger_url': _url('utopic-proposed', 'flo'),
                'num-workers': 2,
            },
            {
                'name': 'manta',
                'slave-label': 'daily-manta',
                'trigger_url': _url('utopic-proposed', 'manta'),
                'num-workers': 2,
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
                'trigger_url': _url('utopic-proposed-customized', 'mako'),
            },
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="--bootstrap --developer-mode'
                     '--channel ubuntu-touch/utopic-proposed-customized"'
    },
]


MATRIX = {
    'trusty': TRUSTY_MATRIX,
    'utopic': UTOPIC_MATRIX,
}
