#!/usr/bin/python

import os
import contextlib
import time


_namespace = os.environ.get('STATSD_KEY')
if _namespace:
    from txstatsd.client import UdpStatsDClient
    from txstatsd.metrics.timermetric import TimerMetric
    from txstatsd.metrics.gaugemetric import GaugeMetric
    _host = os.environ.get('SERVER', 'snakefruit.canonical.com')
    _port = int(os.environ.get('PORT', '10041'))
    _client = UdpStatsDClient(_host, _port)
    _client.connect()


@contextlib.contextmanager
def time_it(key):
    start = time.time()
    try:
        yield
    finally:
        if _namespace:
            m = TimerMetric(_client, _namespace + '.' + key)
            m.mark(time.time() - start)


def gauge_it(key, array):
    val = 0
    if array:
        val = len(array)
    if _namespace:
        GaugeMetric(_client, _namespace + '.' + key).mark(val)
