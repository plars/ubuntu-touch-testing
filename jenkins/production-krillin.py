# The configuration matrix of our staging device testing

JENKINS = 'http://dev-jenkins.ubuntu-ci:8080/'

UTOPIC_MATRIX = [
    {
        'image-type': 'touch_stable',
        'statsd-key': 'ubuntu-ci.daily-image.staging',
        'include-qa': True,
        'dashboard-host': 'dashboard.ubuntu-ci',
        'dashboard-port': '8080',
        'dashboard-user': 'ci-bot',
        'devices': [
            {
                'name': 'krillin',
                'slave-label': 'krillin',
                'trigger_url': 'http://system-image.ubuntu.com/ubuntu-touch/ubuntu-rtm/14.09-proposed/krillin/index.json',
                'num-workers': 2,
            }
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="--bootstrap --developer-mode '
            '--channel=ubuntu-touch/ubuntu-rtm/14.09-proposed"'
    },
    {
        'image-type': 'touch',
        'statsd-key': 'ubuntu-ci.daily-image.staging',
        'include-qa': True,
        'dashboard-host': 'dashboard.ubuntu-ci',
        'dashboard-port': '8080',
        'dashboard-user': 'ci-bot',
        'devices': [
            {
                'name': 'krillin',
                'slave-label': 'krillin',
                'trigger_url': 'http://system-image.ubuntu.com/ubuntu-touch/utopic-proposed/krillin/index.json',
                'num-workers': 4,
            }
        ],
    },
]

MATRIX = {
    'utopic': UTOPIC_MATRIX,
}
