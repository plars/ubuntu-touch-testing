# The configuration matrix of our production device testing

JENKINS = 'http://q-jenkins.ubuntu-ci:8080'


def _url(channel, device):
    return 'http://system-image.ubuntu.com/%s/%s/index.json' \
           % (channel, device)


TRUSTY_MATRIX = [
    {
        'image-type': 'touch_custom_demo',
        'include-qa': True,
        'dashboard-host': 'ci.ubuntu.com',
        'dashboard-port': '80',
        'dashboard-user': 'doanac',
        'devices': [
            {
                'name': 'mako',
                'slave-label': 'daily-mako',
                'trigger_url': _url('trusty-proposed-customized-demo', 'mako'),
            },
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="ubuntu-system -b '
                     '--channel ubuntu-touch/trusty-proposed-customized-demo"'
    },
]

MATRIX = {
    'trusty': TRUSTY_MATRIX,
}
