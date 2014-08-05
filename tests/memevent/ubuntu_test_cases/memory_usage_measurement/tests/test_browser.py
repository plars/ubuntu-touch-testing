
from testtools.matchers import Equals
from webbrowser_app.tests import BrowserTestCaseBase

from ubuntu_test_cases.memory_usage_measurement.tests import MemoryUsageTests
from ubuntu_test_cases.memory_usage_measurement.matchers import (
    Eventually,
)


class BrowserMemoryTestCase(BrowserTestCaseBase, MemoryUsageTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass("webbrowser-app")

    # Override this method so we can store the pid used.
    def launch_test_application(self, application, *arguments, **kwargs):
        launched_app = super().launch_test_application(
            application,
            *arguments,
            **kwargs
        )
        self._browser_pid = launched_app.pid
        return launched_app

    def test_launch_webbrowser(self):
        """Simple test, browser launched."""
        with self.smem.probe('Browser started'):
            self.assertThat(self.main_window.visible, Eventually(Equals(True)))
            self.smem.follow(self._browser_pid)

    def test_navigate_to_url(self):
        with self.smem.probe('Browser finished loading'):
            self.assertThat(self.main_window.visible, Eventually(Equals(True)))
            url = 'http://acid3.acidtests.org/'
            self.go_to_url(url)
            self.assert_page_eventually_loaded(url)
            self.smem.follow(self._browser_pid)
