# The configuration matrix of our production device testing

JENKINS = 'http://localhost:8080'

_devices = [
    {'name': 'mako-doanac', 'serial': '00963b879612414a'},
    {'name': 'grouper-doanac', 'serial': '015d1884b20c1c0f'},
]


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
        'node-label': 'mako-doanac',
        'devices': _devices,
    },
    {
        'image-type': 'custom',
        'node-label': 'mako-doanac',
        'devices': _devices,
        'filter': _custom_test_filter,
        'IMAGE_OPT': 'export IMAGE_OPT="--ubuntu-bootstrap --skip-utah '
                     '--developer-mode --channel devel-customized"'
    },
]
