# The configuration matrix of our production device testing

JENKINS = 'http://10.97.0.1:8080'

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
]
