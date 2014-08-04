import logging
import os
from glob import glob

from camera_app.emulators.main_window import MainWindow as CameraWindow
from testtools.matchers import Equals, HasLength

# from ubuntuuitoolkit.emulators import UbuntuUIToolkitEmulatorBase

from ubuntu_test_cases.memory_usage_measurement.tests import MemoryUsageTests
from ubuntu_test_cases.memory_usage_measurement.matchers import (
    Eventually,
)

LOGGER = logging.getLogger(__file__)


class CameraMemoryUsageTests(MemoryUsageTests):
    IMAGE_FILENAME_PATTERN = os.path.expanduser('~/Pictures/camera/image*')

    def setUp(self):
        super().setUp("camera-app")

    def test_camera_usage(self):
        # camera = CameraApp(self)
        with self.smem.probe('Camera app started'):
            self.launch()
            # self.smem.pids.append(self.app.pid)
            self.smem.follow(self.app.pid, "camera-app")

        with self.smem.probe('Camera app picture taken'):
            self.take_picture()

    def _remove_image_files(self):
        """Remove all image files.

        This is useful not only to cleanup, but also to check that just one
        image file has been written to disk.

        """
        for filename in glob(self.IMAGE_FILENAME_PATTERN):
            LOGGER.debug('Removing image file: {}'.format(filename))
            os.remove(filename)

    def launch(self):
        """Launch application."""
        args = [
            'camera-app',
            '--fullscreen',
            ('--desktop_file_hint='
             '/usr/share/applications/camera-app.desktop'),
        ]
        self.app = self.launch_test_application(*args, app_type='qt')
        self.window = CameraWindow(self.app)

    def take_picture(self):
        """Click on the exposure button to take picture."""
        self._remove_image_files()

        exposure_button = self.window.get_exposure_button()
        self.assertThat(exposure_button.enabled, Eventually(Equals(True)))

        LOGGER.debug('Taking picture...')
        self.pointer.move_to_object(exposure_button)
        self.pointer.click()

        # Wait for image file to be produced before memory usage measurement
        self.assertThat(
            lambda: glob(self.IMAGE_FILENAME_PATTERN),
            Eventually(HasLength(1))
        )
