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


MATRIX = [
    {
        'image-type': 'ro',
        'node-label': 'phoenix',
        'devices': [
            {'name': 'mako-05'},
            {'name': 'maguro-02'},
        ],
    },
    {
        'image-type': 'mir',
        'node-label': 'phoenix',
        'devices': [
            {'name': 'mako-02'},
            {'name': 'maguro-01'},
        ],
    },
    {
        'image-type': 'custom',
        'node-label': 'phoenix',
        'devices': [
            {'name': 'mako-11'},
        ],
        'filter': _custom_test_filter,
        'IMAGE_OPT': 'export IMAGE_OPT="ubuntu-system '
                     '--channel devel-customized"'
    },
]
