from gallery_app.tests.test_photos_view import TestPhotosView

from ubuntu_test_cases.memory_usage_measurement.tests import MemoryUsageTests


class GalleryMemoryTestCase(MemoryUsageTests):

    def setUp(self):
        super().setUp("gallery-app")

    def test_open_photo(self):
        self.memtest_run_test(
            TestPhotosView,
            'test_open_photo',
            'Gallery app open picture'
        )
