from autopilot.platform import model

from testtools.matchers import Contains, Equals
from webbrowser_app.emulators.browser import Browser
from ubuntuuitoolkit.emulators import UbuntuUIToolkitEmulatorBase

from ubuntu_test_cases.memory_usage_measurement.tests import MemoryUsageTests
from ubuntu_test_cases.memory_usage_measurement.matchers import (
    Eventually,
)


class BrowserMemoryUsageTests(MemoryUsageTests):
    def setUp(self):
        super().setUp("webbrowser-app")

    def test_browser_usage(self):
        # browser = BrowserApp(self)
        with self.smem.probe('Browser started'):
            self.launch()
            # self.smem.pids.append(self.app.pid)
            self.smem.follow(self.app.pid, "webbrowser-app")

        with self.smem.probe('Browser finished loading'):
            url = 'http://acid3.acidtests.org/'
            self.go_to_url(url)
            self.assert_page_eventually_loaded(url)

    def launch(self):
        """Launch application."""
        args = [
            'webbrowser-app',
            '--fullscreen',
            ('--desktop_file_hint='
             '/usr/share/applications/webbrowser-app.desktop'),
        ]
        self.app = self.launch_test_application(
            *args,
            app_type='qt',
            emulator_base=UbuntuUIToolkitEmulatorBase
        )
        self.window = self.app.select_single(Browser)
        self.window.visible.wait_for(True)

    def assert_page_eventually_loaded(self, url):
        """Make sure page is eventually loaded."""
        webview = self.window.get_current_webview()
        self.assertThat(webview.url, Eventually(Equals(url)))
        # loadProgress == 100 ensures that a page has actually loaded
        self.assertThat(webview.loadProgress, Eventually(Equals(100)))
        self.assertThat(webview.loading, Eventually(Equals(False)))

    def go_to_url(self, url):
        self.clear_address_bar()
        self.type_in_address_bar(url)
        self.keyboard.press_and_release("Enter")
        self.assert_osk_eventually_hidden()

    def clear_address_bar(self):
        self.focus_address_bar()
        address_bar = self.window.get_chrome().get_address_bar()
        clear_button = address_bar.get_clear_button()
        self.pointer.click_object(clear_button)
        text_field = address_bar.get_text_field()
        self.assertThat(text_field.text, Eventually(Equals("")))

    def focus_address_bar(self):
        address_bar = self.window.get_chrome().get_address_bar()
        self.pointer.click_object(address_bar)
        self.assertThat(address_bar.activeFocus, Eventually(Equals(True)))
        self.assert_osk_eventually_shown()

    def assert_osk_eventually_shown(self):
        if model() != 'Desktop':
            keyboardRectangle = self.window.get_keyboard_rectangle()
            self.assertThat(
                keyboardRectangle.state,
                Eventually(Equals("shown"))
            )

    def assert_osk_eventually_hidden(self):
        if model() != 'Desktop':
            keyboardRectangle = self.window.get_keyboard_rectangle()
            self.assertThat(
                keyboardRectangle.state,
                Eventually(Equals("hidden"))
            )

    def type_in_address_bar(self, text):
        address_bar = self.window.get_chrome().get_address_bar()
        self.assertThat(address_bar.activeFocus, Eventually(Equals(True)))
        self.keyboard.type(text)
        text_field = address_bar.get_text_field()
        self.assertThat(text_field.text, Eventually(Contains(text)))
