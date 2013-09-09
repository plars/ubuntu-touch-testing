"""Measure touch applications memory usage."""

import json
import logging

from autopilot.testcase import AutopilotTestCase

from ubuntu_test_cases.memory_usage_measurement.apps.browser import BrowserApp
from ubuntu_test_cases.memory_usage_measurement.apps.camera import CameraApp
from ubuntu_test_cases.memory_usage_measurement.apps.gallery import GalleryApp
from ubuntu_test_cases.memory_usage_measurement.apps.media_player import (
    MediaPlayerApp,
)
from ubuntu_test_cases.memory_usage_measurement.probes import SmemProbe

LOGGER = logging.getLogger(__file__)


class MemoryUsageTests(AutopilotTestCase):

    """Event based memory usage measurement scenario."""

    def test_scenario(self):
        """Scenario that takes measurements on some events."""
        self.smem = SmemProbe()

        # Make sure report is written with the data collected
        # even if the test failed to complete
        self.addCleanup(self._write_report)

        browser = BrowserApp(self)
        with self.smem.probe('Browser started'):
            browser.launch()
            self.smem.pids.append(browser.app.pid)

        with self.smem.probe('Browser finished loading'):
            url = 'http://www.cnn.com/'
            browser.go_to_url(url)
            browser.assert_page_eventually_loaded(url)

        camera = CameraApp(self)
        with self.smem.probe('Camera app started'):
            camera.launch()
            self.smem.pids.append(camera.app.pid)

        with self.smem.probe('Camera app picture taken'):
            camera.take_picture()

        with self.smem.probe('Gallery app started'):
            gallery = GalleryApp(self)
            gallery.launch()
            self.smem.pids.append(gallery.app.pid)

        with self.smem.probe('Media player app started'):
            media_player = MediaPlayerApp(self)
            media_player.launch()
            self.smem.pids.append(media_player.app.pid)

        with self.smem.probe('Media player app finished playback'):
            media_player = MediaPlayerApp(self)
            media_player.launch('small.mp4')
            self.smem.pids.append(media_player.app.pid)
            media_player.assert_playback_finished()

        summary_msg = '\n'.join(
            ['- {}: {}'.format(event, pids)
             for event, pids in self.smem.threshold_exceeded_summary])
        self.assertListEqual(
            self.smem.threshold_exceeded_summary,
            [],
            'Threshold(s) exceded:\n{}'.format(summary_msg))

    def _write_report(self):
        """Write report to to results directory."""
        report_filename = '/var/cache/utah-probes/memory_usage.json'
        with open(report_filename, 'w') as report_file:
            json.dump(self.smem.report, report_file,
                      indent=4, sort_keys=True)
            LOGGER.debug('Report written to {}'.format(report_file.name))
