"""Event based memory usage measurements test cases."""

import json
import logging

from autopilot.testcase import AutopilotTestCase
from autopilot.input import Mouse, Pointer, Touch
from autopilot.platform import model

from ubuntu_test_cases.memory_usage_measurement.probes import SmemProbe

LOGGER = logging.getLogger(__file__)


class MemoryUsageTests(AutopilotTestCase):

    """Event based memory usage measurement scenario."""

    def setUp(self, app_name):
        super().setUp()
        """Scenario that takes measurements on some events."""

        if model() == 'Desktop':
            input_device = Mouse.create()
        else:
            input_device = Touch.create()
        self.pointer = Pointer(input_device)

        self.smem = SmemProbe()

        # Make sure report is written with the data collected
        # even if the test failed to complete
        self.addCleanup(self._write_report, app_name)

    def _write_report(self, app_name):
        """Write report to to results directory."""
        report_filename = '/tmp/memory_usage_{}.json'.format(app_name)
        with open(report_filename, 'w') as report_file:
            json.dump(self.smem.report, report_file,
                      indent=4, sort_keys=True)
            LOGGER.debug('Report written to {}'.format(report_file.name))
