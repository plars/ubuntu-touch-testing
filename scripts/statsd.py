#!/usr/bin/python

import os
import contextlib
import socket
import time


_namespace = os.environ.get('STATSD_KEY')
if _namespace:
    _host = os.environ.get('SERVER', 'snakefruit.canonical.com')
    _port = int(os.environ.get('PORT', '10041'))
    _conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def _statsd(val):
    if _namespace:
        val = _namespace + '.' + val
        _conn.sendto(val, (_host, _port))


@contextlib.contextmanager
def time_it(key):
    start = time.time()
    try:
        yield
    finally:
        _statsd('%s:%d|ms' % (key, time.time() - start))


def gauge_it(key, array):
    val = 0
    if array:
        val = len(array)
    _statsd('%s:%d|g' % (key, val))
