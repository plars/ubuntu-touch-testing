import logging

from camera_app.tests.test_capture import TestCapture

from ubuntu_test_cases.memory_usage_measurement.tests import MemoryUsageTests

LOGGER = logging.getLogger(__file__)


class CameraMemoryTestCase(MemoryUsageTests):

    def setUp(self):
        super().setUp("camera-app")

    def test_take_picture(self):
        self.memtest_run_test(
            TestCapture,
            'test_take_picture',
            "Camera app picture taken",
        )
