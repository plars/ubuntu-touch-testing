from testtools.matchers import Equals
from webbrowser_app.tests import BrowserTestCaseBase

from ubuntu_test_cases.memory_usage_measurement.tests import MemoryUsageTests
from ubuntu_test_cases.memory_usage_measurement.matchers import (
    Eventually,
)


class BrowserMemoryTestCase(MemoryUsageTests):
    def setUp(self):
        super().setUp('webbrowser-app')

    def test_webbrowser_navigation(self):
        # Use the browsers autopilot test cases methods.
        class SingleTestCaseBase(BrowserTestCaseBase):
            def test_navigate_to_url(self):
                self.assertThat(
                    self.main_window.visible,
                    Eventually(Equals(True))
                )
                url = 'http://acid3.acidtests.org/'
                self.go_to_url(url)
                self.assert_page_eventually_loaded(url)

        self.memtest_run_test(
            SingleTestCaseBase,
            "test_navigate_to_url",
            "Navigate to url"
        )
