# The configuration matrix of our production device testing

JENKINS = 'http://10.97.0.1:8080'


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
                'trigger_url': _url('trusty-proposed', 'mako'),
            },
            {
                'name': 'maguro-02',
                'trigger_url': _url('trusty-proposed', 'maguro'),
            },
        ],
    },
    {
        'image-type': 'touch',
        'node-label': 'phoenix',
        'devices': [
            {
                'name': 'mako-02',
                'trigger_url': _url('trusty-proposed', 'mako'),
            },
            {
                'name': 'maguro-01',
                'trigger_url': _url('trusty-proposed', 'maguro'),
            },
        ],
    },
    {
        'image-type': 'touch_custom',
        'node-label': 'phoenix',
        'devices': [
            {
                'name': 'mako-11',
                'trigger_url': _url('trusty-proposed-customized', 'mako'),
            },
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="ubuntu-system '
                     '--channel trusty-proposed-customized"'
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
                'name': 'maguro-03',
                'trigger_url': _url('saucy-proposed', 'maguro'),
            },
        ],
        'IMAGE_OPT': 'export IMAGE_OPT="ubuntu-system '
                     '--channel saucy-proposed"'
    },
]

MATRIX = {
    'trusty': TRUSTY_MATRIX,
    'saucy': SAUCY_MATRIX,
}
