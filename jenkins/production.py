# The configuration matrix of our production device testing

JENKINS = 'http://q-jenkins.ubuntu-ci:8080'


def _url(channel, device):
    return 'http://system-image.ubuntu.com/ubuntu-touch/%s/%s/index.json' \
           % (channel, device)


WILY_MATRIX = [
    {
        'image-type': 'touch',
        'statsd-key': 'ubuntu-ci.daily-image.production',
        'include-qa': True,
        'dashboard-host': 'ci.ubuntu.com',
        'dashboard-port': '80',
        'dashboard-user': 'uci-bot',
        'devices': [
            {
                'name': 'mako',
                'slave-label': 'daily-mako',
                'trigger_url': _url('devel-proposed/ubuntu', 'mako'),
                'num-workers': 3,
            },
            {
                'name': 'flo',
                'slave-label': 'daily-flo',
                'trigger_url': _url('devel-proposed/ubuntu', 'flo'),
                'num-workers': 2,
            },
            {
                'name': 'manta',
                'slave-label': 'daily-manta',
                'trigger_url': _url('devel-proposed/ubuntu', 'manta'),
                'num-workers': 2,
            },
        ],
    },
]

VIVID_MATRIX = [
    {
        'image-type': 'touch_stable',
        'statsd-key': 'ubuntu-ci.daily-image.production',
        'include-qa': True,
        'dashboard-host': 'ci.ubuntu.com',
        'dashboard-port': '80',
        'dashboard-user': 'uci-bot',
        'devices': [
            {
                'name': 'mako',
                'slave-label': 'daily-mako',
                'trigger_url': _url('rc-proposed/ubuntu', 'mako'),
                'num-workers': 3,
            },
            {
                'name': 'flo',
                'slave-label': 'daily-flo',
                'trigger_url': _url('rc-proposed/ubuntu', 'flo'),
                'num-workers': 2,
            },
            {
                'name': 'manta',
                'slave-label': 'daily-manta',
                'trigger_url': _url('rc-proposed/ubuntu', 'manta'),
                'num-workers': 2,
            },
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="--bootstrap --developer-mode '
                     '--channel ubuntu-touch/rc-proposed/ubuntu"'
    },
    {
        'image-type': 'touch_custom',
        'statsd-key': 'ubuntu-ci.daily-image.production',
        'include-qa': False,
        'dashboard-host': 'ci.ubuntu.com',
        'dashboard-port': '80',
        'dashboard-user': 'uci-bot',
        'devices': [
            {
                'name': 'mako',
                'slave-label': 'daily-mako',
                'trigger_url': _url('utopic-proposed-customized', 'mako'),
            },
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="--bootstrap --developer-mode '
                     '--channel ubuntu-touch/utopic-proposed-customized"'
    },
]


MATRIX = {
    'vivid': VIVID_MATRIX,
    'wily': WILY_MATRIX,
}
