# The configuration matrix of our production device testing

JENKINS = 'http://10.97.0.1:8080'


def _custom_test_filter(common_tests, mktest_func):
    tests = []
    test_set = [
        'install-and-boot',
        'default',
        'unity8-autopilot',
        'webbrowser-app-autopilot',
    ]

    tests = [t for t in common_tests if t.name in test_set]
    tests.insert(1, mktest_func('customizations'))
    return tests


def _sf4p_test_filter(common_tests, mktest_func):
    tests = []
    test_set = [
        'install-and-boot',
        'default',
        'unity8-autopilot',
    ]

    tests = [t for t in common_tests if t.name in test_set]
    tests.insert(1, mktest_func('customizations'))
    return tests


def _url(channel, device):
    return 'http://system-image.ubuntu.com/%s/%s/index.json' \
           % (channel, device)


TRUSTY_MATRIX = [
    {
        'image-type': 'touch_sf4p',
        'node-label': 'phoenix',
        'devices': [
            {
                'name': 'mako-05',
                'trigger_url': _url('devel-proposed', 'mako'),
            },
            {
                'name': 'maguro-02',
                'trigger_url': _url('devel-proposed', 'maguro'),
            },
        ],
        'filter': _sf4p_test_filter,
    },
    {
        'image-type': 'touch',
        'node-label': 'phoenix',
        'devices': [
            {
                'name': 'mako-02',
                'trigger_url': _url('devel-proposed', 'mako'),
            },
            {
                'name': 'maguro-01',
                'trigger_url': _url('devel-proposed', 'maguro'),
            },
        ],
    },
    {
        'image-type': 'touch_custom',
        'node-label': 'phoenix',
        'devices': [
            {
                'name': 'mako-11',
                'trigger_url': _url('devel-proposed-customized', 'mako'),
            },
        ],
        'filter': _custom_test_filter,
        'IMAGE_OPT': 'export IMAGE_OPT="ubuntu-system '
                     '--channel devel-proposed-customized"'
    },
]

SAUCY_MATRIX = [
    {
        'image-type': 'touch_mir',
        'node-label': 'phoenix',
        'devices': [
            {
                # mako-11 should be the least utilized trusty device
                'name': 'mako-11',
                'trigger_url': _url('saucy-proposed', 'mako'),
            },
            {
                # maguro-02 should be the least utilized trusty device
                'name': 'maguro-02',
                'trigger_url': _url('saucy-proposed', 'maguro'),
            },
        'IMAGE_OPT': 'export IMAGE_OPT="ubuntu-system '
                     '--channel saucy-proposed"'
        ],
    },
]

MATRIX = {
    'trusty': TRUSTY_MATRIX,
    'saucy': SAUCY_MATRIX,
}
