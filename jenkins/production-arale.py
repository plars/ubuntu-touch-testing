# The configuration matrix of our staging device testing

JENKINS = 'http://dev-jenkins.ubuntu-ci:8080/'

VIVID_MATRIX = [
    {
        'image-type': 'touch_stable',
        'statsd-key': 'ubuntu-ci.daily-image.staging',
        'include-qa': True,
        'dashboard-host': 'dashboard.ubuntu-ci',
        'dashboard-port': '8080',
        'dashboard-user': 'ci-bot',
        'devices': [
            {
                'name': 'arale',
                'slave-label': 'arale',
                'trigger_url': 'http://system-image.ubuntu.com/'
                               'ubuntu-touch/rc-proposed/meizu.en/'
                               'arale/index.json',
                'num-workers': 4,
            }
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="--bootstrap --developer-mode '
                     '--channel=ubuntu-touch/rc-proposed/meizu.en '
                     '--device=arale"',
    },
]

WILY_MATRIX = [
    {
        'image-type': 'touch',
        'statsd-key': 'ubuntu-ci.daily-image.staging',
        'include-qa': True,
        'dashboard-host': 'dashboard.ubuntu-ci',
        'dashboard-port': '8080',
        'dashboard-user': 'ci-bot',
        'devices': [
            {
                'name': 'arale',
                'slave-label': 'arale',
                'trigger_url': 'http://system-image.ubuntu.com/'
                               'ubuntu-touch/devel-proposed/meizu.en/'
                               'arale/index.json',
                'num-workers': 4,
            }
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="--bootstrap --developer-mode '
                     '--channel=ubuntu-touch/devel-proposed/meizu.en '
                     '--device=arale"',
    },
]

MATRIX = {
    'wily': WILY_MATRIX,
    'vivid': VIVID_MATRIX,
}
