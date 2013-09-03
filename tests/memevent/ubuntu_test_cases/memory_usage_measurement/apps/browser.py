"""Browser application to write autopilot test cases easily."""

from testtools.matchers import Contains, Equals

from ubuntuuitoolkit.emulators import UbuntuUIToolkitEmulatorBase
from webbrowser_app.emulators.browser import Browser

from ubuntu_test_cases.memory_usage_measurement.apps import App
from ubuntu_test_cases.memory_usage_measurement.matchers import (
    DoesNotChange,
    Eventually,
)


class BrowserApp(App):

    """Browser application."""

    TYPING_DELAY = 0.01

    def assert_chrome_eventually_hidden(self):
        """Make sure chrome is eventually hidden."""

        toolbar = self.window.get_toolbar()
        self.tc.assertThat(toolbar.opened, Eventually(Equals(False)))
        self.tc.assertThat(toolbar.animating, Eventually(Equals(False)))

    def assert_page_eventually_loaded(self, url):
        """Make sure page is eventually loaded."""
        webview = self.window.get_current_webview()
        self.tc.assertThat(webview.url, Eventually(Equals(url)))
        # loadProgress == 100 ensures that a page has actually loaded
        self.tc.assertThat(webview.loadProgress, Eventually(Equals(100)))
        self.tc.assertThat(webview.loading, Eventually(Equals(False)))

    def clear_address_bar(self):
        """Clear address bar."""
        self.focus_address_bar()
        clear_button = self.window.get_address_bar_clear_button()
        self.tc.assertThat(lambda: (clear_button.x,
                                    clear_button.y,
                                    clear_button.y),
                           Eventually(DoesNotChange()))
        self.pointer.move_to_object(clear_button)
        self.pointer.click()
        text_field = self.window.get_address_bar_text_field()
        self.tc.assertThat(text_field.text, Eventually(Equals("")))

    def ensure_chrome_is_hidden(self):
        """Make sure chrome is hidden."""
        webview = self.window.get_current_webview()
        self.pointer.move_to_object(webview)
        self.pointer.click()
        self.assert_chrome_eventually_hidden()

    def focus_address_bar(self):
        """Make sure address bar is focused."""
        address_bar = self.window.get_address_bar()
        self.pointer.move_to_object(address_bar)
        self.pointer.click()
        self.tc.assertThat(address_bar.activeFocus, Eventually(Equals(True)))

    def go_to_url(self, url):
        """Go to given url.

        :param url: URL that should be loaded in the browser
        :type url: str

        """
        self.ensure_chrome_is_hidden()
        self.window.open_toolbar()
        self.clear_address_bar()
        self.type_in_address_bar(url)
        self.keyboard.press_and_release("Enter")

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

    def type_in_address_bar(self, text):
        """Type text in address bar.

        :param text: Text to be typed in the address bar.
        :type text: str

        """
        address_bar = self.window.get_address_bar()
        self.tc.assertThat(address_bar.activeFocus, Eventually(Equals(True)))
        self.keyboard.type(text, delay=self.TYPING_DELAY)
        text_field = self.window.get_address_bar_text_field()
        self.tc.assertThat(text_field.text, Eventually(Contains(text)))
