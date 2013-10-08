# The configuration matrix of our production device testing

JENKINS = 'http://localhost:8080'

MATRIX = [
    {
        'image-type': 'ro',
        'node-label': 'mako-doanac',
        'devices': [
            {'name': 'mako-doanac'},
            {'name': 'grouper-doanac'},
        ],
    },
]
