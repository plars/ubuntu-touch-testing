# The configuration matrix of our production device testing

JENKINS = 'http://10.97.9.20:8080'

MATRIX = [
    {
        'image-type': 'ro',
        'node-label': 'ashes',
        'devices': [
            {'name': 'mako-06'},
        ],
    },
]
