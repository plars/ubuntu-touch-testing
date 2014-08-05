"""Event based memory usage measurements test cases."""

import json
import logging

from testtools import TestCase

from ubuntu_test_cases.memory_usage_measurement.probes import SmemProbe

LOGGER = logging.getLogger(__file__)


class MemoryUsageTestsMixin(object):
    def launch_test_application(self, application, *arguments, **kwargs):
        self.smem.start("Application Launch")
        launched_app = super().launch_test_application(
            application,
            *arguments,
            **kwargs
        )
        self.smem.follow(launched_app.pid)
        self.smem.stop("Application Launch")
        self.smem.start(self.eventname)

        self.addCleanup(self.smem.stop, self.eventname)
        return launched_app


class MemoryUsageTests(TestCase):

    """Event based memory usage measurement scenario."""

    def setUp(self, app_name):
        super().setUp()
        self.app_name = app_name
        self.smem = SmemProbe()

    def memtest_run_test(self, test_class, test_id, eventname):
        print("Overriding the method, and running the test:")

        TestClass = type(
            "MemTestTestClass",
            (MemoryUsageTestsMixin, test_class),
            {'smem': self.smem, 'eventname': eventname}
        )

        t = TestClass(test_id)
        result = t.run()
        if not result.wasSuccessful():
            raise Exception()
        self.addCleanup(self._write_report)

    def _write_report(self):
        test_id_name = self.id().split('.')[-1]
        report_filename = '/tmp/memory_usage_{}.{}.json'.format(
            self.app_name,
            test_id_name
        )
        with open(report_filename, 'w') as report_file:
            json.dump(
                self.smem.report,
                report_file,
                indent=4,
                sort_keys=True
            )
            LOGGER.debug('Report written to {}'.format(report_file.name))
