# The configuration matrix of our staging device testing

JENKINS = 'http://dev-jenkins.ubuntu-ci:8080/'

UTOPIC_MATRIX = [
    {
        'image-type': 'touch',
        'statsd-key': 'ubuntu-ci.daily-image.staging',
        'include-qa': True,
        'dashboard-host': 'dashboard.ubuntu-ci',
        'dashboard-port': '8080',
        'dashboard-user': 'ci-bot',
        'devices': [
            {
                'name': 'mako',
                'slave-label': 'mako',
                #'trigger_url': 'http://system-image.ubuntu.com/utopic-proposed/mako/index.json',
            }
        ],
    },
    {
        'image-type': 'touch_stable',
        'statsd-key': 'ubuntu-ci.daily-image.staging',
        'include-qa': True,
        'dashboard-host': 'dashboard.ubuntu-ci',
        'dashboard-port': '8080',
        'dashboard-user': 'ci-bot',
        'devices': [
            {
                'name': 'mako',
                'slave-label': 'mako',
                #'trigger_url': 'http://system-image.ubuntu.com/utopic-proposed/mako/index.json',
            }
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="--bootstrap --developer-mode '
                     '--channel ubuntu-touch/staging-stable-proposed"'
    },
]

MATRIX = {
    'utopic': UTOPIC_MATRIX,
}
