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

    @classmethod
    def setUpClass(cls, appname):
        cls._app_id_name = appname
        cls.smem = SmemProbe()

    @classmethod
    def tearDownClass(cls):
        """Write report to to results directory."""

        report_filename = '/tmp/memory_usage_{}.json'.format(cls._app_id_name)
        with open(report_filename, 'w') as report_file:
            json.dump(
                cls.smem.report,
                report_file,
                indent=4,
                sort_keys=True
            )
            LOGGER.debug('Report written to {}'.format(report_file.name))

    def setUp(self):
        super().setUp()
        """Scenario that takes measurements on some events."""

        if model() == 'Desktop':
            input_device = Mouse.create()
        else:
            input_device = Touch.create()
        self.pointer = Pointer(input_device)
