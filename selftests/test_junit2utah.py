import StringIO
import os
import sys
import unittest

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, '../scripts'))

import junit2utah

RESULT = '''
<testsuite errors="0" failures="1" name="" tests="4" time="0.001">
<testcase classname="classname" name="testFails" time="0.000">
<failure type="testtools.testresult.real._StringException">
testtools.testresult.real._StringException: Traceback (most recent call last):
  File "junit2utah.py", line 14, in testFails
    self.assertFalse(True)
  File "/usr/lib/python2.7/unittest/case.py", line 418, in assertFalse
    raise self.failureException(msg)
AssertionError: True is not false
</failure>
</testcase>
<testcase classname="classname" name="testPasses" time="0.100"/>
<testcase classname="classname" name="testPasses2" time="0.200"/>
<testcase classname="classname" name="testSkip" time="0.000">
<skip>ensure skip works</skip>
</testcase>
</testsuite>
'''


class TestJunit2Utah(unittest.TestCase):
    def testFull(self):
        stream = StringIO.StringIO(RESULT)
        results = junit2utah._get_results(stream)
        self.assertEquals(3, results['passes'])
        self.assertEquals(1, results['failures'])
        self.assertEquals(0, results['errors'])

        tcs = results['commands']
        self.assertEqual('classname', tcs[0]['testsuite'])
        self.assertEqual('testFails', tcs[0]['testcase'])
        self.assertIn('AssertionError', tcs[0]['stderr'])

        self.assertEqual('0.200', tcs[2]['time_delta'])

        self.assertEqual('classname', tcs[3]['testsuite'])
        self.assertEqual('testSkip', tcs[3]['testcase'])
        self.assertEqual('ensure skip works', tcs[3]['stdout'])
