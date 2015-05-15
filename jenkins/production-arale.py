# The configuration matrix of our staging device testing

JENKINS = 'http://dev-jenkins.ubuntu-ci:8080/'

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
                'trigger_url': 'https://sis.capomastro.canonical.com/'
                               'ubuntu-touch/tangxi/devel-proposed/'
                               'arale/index.json',
                'num-workers': 4,
            }
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="--bootstrap --developer-mode '
                     '--channel=ubuntu-touch/tangxi/devel-proposed '
                     '--device=arale"',
        'IMAGE_SERVER': 'export IMAGE_SERVER='
                        '"--server https://sis.capomastro.canonical.com"'
    },
]

MATRIX = {
    'wily': WILY_MATRIX,
}
