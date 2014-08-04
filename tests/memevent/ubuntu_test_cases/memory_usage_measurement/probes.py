"""Probes used to take measurements4 while the tests are executed."""

import itertools
import logging
import os
import re
import subprocess

from contextlib import contextmanager
from time import time

LOGGER = logging.getLogger(__file__)


class SmemProbe(object):

    """Memory usage probe."""

    BINARY = os.path.join(os.path.dirname(__file__), 'smem-tabs')
    THRESHOLDS = {
        'foreground': 262144,  # 256MB
        'background': 131072,  # 128MB
    }

    def __init__(self):
        self.pids = []  # List of pids that should be monitored
        self.readings = []  # List of readings
        self.current_reading = None
        self.threshold_exceeded_summary = []
        self._appname_to_pid = {}

    @contextmanager
    def probe(self, event):
        """Run start and stop methods in a contex manager."""
        self.start(event)
        yield
        self.stop(event)

    def follow(self, pid, app_name=""):
        """Inform probe that we are interested in this pid, optionally assign
        an application name against it for ease of reporting.

        """
        self.pids.append(pid)
        self._appname_to_pid[pid] = app_name

    def start(self, event):
        """Start measurement.

        This method is not actually used, but defined to be consistent with the
        probes API.

        :param event: Event name
        :type event: str
        :returns: None

        """
        LOGGER.debug('smem start: {}'.format(event))
        self.current_reading = {
            'event': event,
            'start_time': time(),
        }

    def stop(self, event):
        """Stop measurement.

        Run smem and get memory usage for a given set PIDs.

        :param event: Event name
        :type event: str
        :returns: None

        """
        LOGGER.debug('smem stop: {}'.format(event))
        LOGGER.debug('Running {!r}...'.format(self.BINARY))
        output = subprocess.check_output(self.BINARY, universal_newlines=True)
        parser = SmemParser()
        pids_info = parser.parse(output)
        threshold_exceeded_pids = self._calculate_threshold_exceeded(pids_info)
        print('{:-^72}'.format(event))
        for pid in self.pids:
            print('PID: {pid}, command: {command}, PSS: {pss}, USS: {uss}'
                  .format(**pids_info[pid]))

        self.current_reading['stop_time'] = time()
        self.current_reading['data'] = pids_info
        self.readings.append(self.current_reading)
        if threshold_exceeded_pids:
            self.threshold_exceeded_summary.append(
                (event, threshold_exceeded_pids))
        self.current_reading = None

    def _calculate_threshold_exceeded(self, pids_info):
        """Calculate thresholds for the given set of pids.

        :param pids_info:
            Memory usage data for a give set of pids.

            ..note::
                This parameter is modified in place to add a delta of the PSS
                and the threshold.
        :type pids_info: list(dict)

        """
        # It's assumed that the pid for the foreground application is the one
        # that was last added to the probe
        foreground_pid = self.pids[-1]
        foreground_threshold = self.THRESHOLDS['foreground']
        background_pids = self.pids[:-1]
        background_threshold = self.THRESHOLDS['background']

        pids_and_thresholds = itertools.chain(
            [(foreground_pid, foreground_threshold)],
            itertools.product(background_pids, [background_threshold]))

        threshold_exceeded_pids = []
        for pid, threshold in pids_and_thresholds:
            if pid in pids_info:
                pid_info = pids_info[pid]
                delta = pid_info['pss'] - threshold
                pid_info['threshold_exceeded'] = delta
                if delta > 0:
                    threshold_exceeded_pids.append(pid)
        return threshold_exceeded_pids

    @property
    def report(self):
        """Return report with all the readings that have been made."""
        return {
            'pids': self.pids,
            'named_pids': self._appname_to_pid,
            'thresholds': self.THRESHOLDS,
            'readings': self.readings}


class SmemParser(object):

    """Parser object to map smem output to data structure."""

    SMEM_LINE = re.compile(
        r'\s*(?P<pid>\d+)'
        r'\s+(?P<user>\w+)'
        r'\s+(?P<command>.+?)'
        r'\s+(?P<swap>\d+)'
        r'\s+(?P<uss>\d+)'
        r'\s+(?P<pss>\d+)'
        r'\s+(?P<rss>\d+)')

    def parse(self, output):
        """Parse smem output.

        :param output: The report printed to stdout by smem
        :type output: str
        :returns: Data structure that can be serialized
        :rtype: dict(dict)

        """
        pids_info = [_f for _f in [self._parse_line(line)
                     for line in output.splitlines()[1:]] if _f]
        return {pid_info['pid']: pid_info for pid_info in pids_info}

    def _parse_line(self, line):
        """Parse a single smem output line.

        :param line:
            A single line containing all the fields to parse for a process.
        :type line: str
        :returns: Data structure with the parsed fields
        :rtype: dict

        """
        match = self.SMEM_LINE.match(line)
        if not match:
            LOGGER.warning('Unable to parse smem output: {}'.format(line))
            return None

        pid_info = match.groupdict()
        for key in ('pid', 'swap', 'uss', 'pss', 'rss'):
            pid_info[key] = int(pid_info[key])
        return pid_info
