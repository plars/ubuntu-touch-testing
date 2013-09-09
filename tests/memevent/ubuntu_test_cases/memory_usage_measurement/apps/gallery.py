"""Gallery application to write autopilot test cases easily."""

import os
import shutil
import tempfile

from ubuntu_test_cases.memory_usage_measurement.apps import App


class GalleryApp(App):

    """Gallery application."""

    SAMPLE_DIR = '/usr/lib/python2.7/dist-packages/gallery_app/data/default'

    def __init__(self, tc):
        super(GalleryApp, self).__init__(tc)
        self.temp_sample_dir = None
        self._copy_sample_dir()

    def _copy_sample_dir(self):
        """Copy sample directory to a temporary location.

        This is useful to provide some default content.

        """
        self.temp_sample_dir = tempfile.mkdtemp(prefix='gallery-app-test-')
        self.tc.addCleanup(shutil.rmtree, self.temp_sample_dir)
        self.temp_sample_dir = os.path.join(self.temp_sample_dir, 'data')
        shutil.copytree(self.SAMPLE_DIR, self.temp_sample_dir)

    def launch(self):
        """Launch the application."""
        args = [
            'gallery-app',
            ('--desktop_file_hint='
             '/usr/share/applications/gallery-app.desktop'),
            self.temp_sample_dir,
        ]
        self.app = self.tc.launch_test_application(*args,
                                                   app_type='qt')
