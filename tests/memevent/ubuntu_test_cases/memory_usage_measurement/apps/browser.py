"""Browser application to write autopilot test cases easily."""

from testtools.matchers import Contains, Equals

from ubuntuuitoolkit.emulators import UbuntuUIToolkitEmulatorBase
from webbrowser_app.emulators.browser import Browser
from autopilot.platform import model

from ubuntu_test_cases.memory_usage_measurement.apps import App
from ubuntu_test_cases.memory_usage_measurement.matchers import (
    Eventually,
)


class BrowserApp(App):

    """Browser application."""

    TYPING_DELAY = 0.01

    def launch(self):
        """Launch application."""
        args = [
            'webbrowser-app',
            '--fullscreen',
            ('--desktop_file_hint='
             '/usr/share/applications/webbrowser-app.desktop'),
        ]
        self.app = self.tc.launch_test_application(
            *args,
            app_type='qt',
            emulator_base=UbuntuUIToolkitEmulatorBase
        )
        self.window = self.app.select_single(Browser)
        self.window.visible.wait_for(True)

    def assert_page_eventually_loaded(self, url):
        """Make sure page is eventually loaded."""
        webview = self.window.get_current_webview()
        self.tc.assertThat(webview.url, Eventually(Equals(url)))
        # loadProgress == 100 ensures that a page has actually loaded
        self.tc.assertThat(webview.loadProgress, Eventually(Equals(100)))
        self.tc.assertThat(webview.loading, Eventually(Equals(False)))

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
        self.tc.assertThat(text_field.text, Eventually(Equals("")))

    def focus_address_bar(self):
        address_bar = self.window.get_chrome().get_address_bar()
        self.pointer.click_object(address_bar)
        self.tc.assertThat(address_bar.activeFocus, Eventually(Equals(True)))
        self.assert_osk_eventually_shown()

    def assert_osk_eventually_shown(self):
        if model() != 'Desktop':
            keyboardRectangle = self.window.get_keyboard_rectangle()
            self.tc.assertThat(
                keyboardRectangle.state,
                Eventually(Equals("shown"))
            )

    def assert_osk_eventually_hidden(self):
        if model() != 'Desktop':
            keyboardRectangle = self.window.get_keyboard_rectangle()
            self.tc.assertThat(
                keyboardRectangle.state,
                Eventually(Equals("hidden"))
            )

    def type_in_address_bar(self, text):
        address_bar = self.window.get_chrome().get_address_bar()
        self.tc.assertThat(address_bar.activeFocus, Eventually(Equals(True)))
        self.keyboard.type(text)
        text_field = address_bar.get_text_field()
        self.tc.assertThat(text_field.text, Eventually(Contains(text)))
