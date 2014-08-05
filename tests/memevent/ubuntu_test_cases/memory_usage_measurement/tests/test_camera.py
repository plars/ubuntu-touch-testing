import logging
import os
from glob import glob

from camera_app.tests import CameraAppTestCase
from testtools.matchers import Equals, HasLength

from ubuntu_test_cases.memory_usage_measurement.tests import MemoryUsageTests
from ubuntu_test_cases.memory_usage_measurement.matchers import (
    Eventually,
)

LOGGER = logging.getLogger(__file__)


class CameraMemoryTestCase(CameraAppTestCase, MemoryUsageTests):

    IMAGE_FILENAME_PATTERN = os.path.expanduser('~/Pictures/camera/image*')

    @classmethod
    def setUpClass(cls):
        super().setUpClass("camera-app")

    # Override this method so we can store the pid used.
    def launch_test_application(self, application, *arguments, **kwargs):
        launched_app = super().launch_test_application(
            application,
            *arguments,
            **kwargs
        )
        self._camera_pid = launched_app.pid
        return launched_app

    def test_launch_camera_app(self):
        """Simple test, camera launched."""
        with self.smem.probe('Camera app started'):
            self.assertThat(
                self.main_window.get_qml_view().visible,
                Eventually(Equals(True))
            )
            self.smem.follow(self._camera_pid)

    def test_take_picture(self):
        self._remove_image_files()

        with self.smem.probe('Camera app picture taken'):
            self.press_exposure_button()

            # Wait for image file to be produced before memory usage
            # measurement
            self.assertThat(
                lambda: glob(self.IMAGE_FILENAME_PATTERN),
                Eventually(HasLength(1))
            )
            self.smem.follow(self._camera_pid)

    def press_exposure_button(self):
        exposure_button = self.main_window.get_exposure_button()
        self.assertThat(exposure_button.enabled, Eventually(Equals(True)))

        LOGGER.debug('Taking picture...')
        self.pointer.move_to_object(exposure_button)
        self.pointer.click()

    def _remove_image_files(self):
        """Remove all image files.

        This is useful not only to cleanup, but also to check that just one
        image file has been written to disk.

        """
        for filename in glob(self.IMAGE_FILENAME_PATTERN):
            LOGGER.debug('Removing image file: {}'.format(filename))
            os.remove(filename)
