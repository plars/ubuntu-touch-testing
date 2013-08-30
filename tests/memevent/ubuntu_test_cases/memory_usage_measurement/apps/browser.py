"""Browser application to write autopilot test cases easily."""

from testtools.matchers import Contains, Equals

from webbrowser_app.emulators.main_window import MainWindow as BrowserWindow

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
        view = self.window.get_qml_view()
        chrome = self.window.get_chrome()
        self.tc.assertThat(lambda: chrome.globalRect[1],
                           Eventually(Equals(view.y + view.height)))

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
        self.reveal_chrome()
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
        self.app = self.tc.launch_test_application(*args, app_type='qt')
        self.window = BrowserWindow(self.app)
        self.tc.assertThat(self.window.get_qml_view().visible,
                           Eventually(Equals(True)))

    def reveal_chrome(self):
        """Reveal chrome."""
        panel = self.window.get_panel()
        distance = self.window.get_chrome().height
        view = self.window.get_qml_view()
        x_line = int(view.x + view.width * 0.5)
        start_y = int(view.y + view.height - 1)
        stop_y = int(start_y - distance)
        self.pointer.drag(x_line, start_y, x_line, stop_y)
        self.tc.assertThat(panel.state, Eventually(Equals('spread')))

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
