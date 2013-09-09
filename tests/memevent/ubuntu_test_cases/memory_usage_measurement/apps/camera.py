"""Camera application to write autopilot test cases easily."""

import logging
import os

from glob import glob

from camera_app.emulators.main_window import MainWindow as CameraWindow
from testtools.matchers import Equals, HasLength

from ubuntu_test_cases.memory_usage_measurement.apps import App
from ubuntu_test_cases.memory_usage_measurement.matchers import Eventually

LOGGER = logging.getLogger(__file__)


class CameraApp(App):

    """Camera application."""

    IMAGE_FILENAME_PATTERN = os.path.expanduser('~/Pictures/image*')

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
        self.app = self.tc.launch_test_application(*args, app_type='qt')
        self.window = CameraWindow(self.app)

    def take_picture(self):
        """Click on the exposure button to take picture."""
        self._remove_image_files()

        exposure_button = self.window.get_exposure_button()
        self.tc.assertThat(exposure_button.enabled, Eventually(Equals(True)))

        LOGGER.debug('Taking picture...')
        self.pointer.move_to_object(exposure_button)
        self.pointer.click()

        # Wait for image file to be produced before memory usage measurement
        self.tc.assertThat(lambda: glob(self.IMAGE_FILENAME_PATTERN),
                           Eventually(HasLength(1)))
