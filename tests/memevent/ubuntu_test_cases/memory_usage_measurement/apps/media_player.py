"""Media player application to write autopilot test cases easily."""

import os

from testtools.matchers import Equals, GreaterThan

from mediaplayer_app.emulators.main_window import (
    MainWindow as MediaPlayerWindow)

from ubuntu_test_cases.memory_usage_measurement.apps import App
from ubuntu_test_cases.memory_usage_measurement.matchers import Eventually


class MediaPlayerApp(App):

    """Media player application."""

    # Default content
    VIDEOS_DIR = 'file:///usr/share/mediaplayer-app/videos/'

    def assert_playback_finished(self):
        """Media player memory usage after playing a file."""
        time_line = self.window.get_object("Slider", "TimeLine.Slider")

        # Time line value isn't set to maximum value after playback is finished
        # (LP: #1190555)
        maximum_value = time_line.maximumValue - 2.0
        self.tc.assertThat(time_line.value,
                           Eventually(GreaterThan(maximum_value)))

    def launch(self, movie_file=None):
        """Launch application.

        :param movie_file:
            Relative path to movie file (uses default content directory as
            root).
        :type movie_file: str

        """
        binary = 'mediaplayer-app'
        args = [
            binary,
            '--fullscreen',
            ('--desktop_file_hint='
             '/usr/share/applications/mediaplayer-app.desktop'),
        ]
        if movie_file:
            args.insert(1, os.path.join(self.VIDEOS_DIR, movie_file))

        self.app = self.tc.launch_test_application(*args, app_type='qt')
        self.window = MediaPlayerWindow(self.app)
        self.tc.assertThat(self.window.get_qml_view().visible,
                           Eventually(Equals(True)))
