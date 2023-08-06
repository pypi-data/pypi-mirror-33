#
# Test runner with Automake "Simple tests" format output.
#
# Copyright (c) 2018 Beta Five Ltd
#
# SPDX-License-Identifier: Apache-2.0
#

import sys
import unittest

class AMTestResult(unittest.TestResult):
    """
    Test result which prints output in automake "Simple tests" format. See
    http://www.gnu.org/software/automake/manual/automake.html#Simple-Tests
    for further details on this format.
    """

    def __init__(self, runner):
        super(AMTestResult, self).__init__()
        self.runner = runner

    def addError(self, test, err):
        super(AMTestResult, self).addError(test, err)
        self.runner.write("ERROR: %s: %s\n" % (str(test), str(err[1])))
        if self.runner.show_tracebacks:
            import traceback
            traceback.print_tb(err[2])

    def addSuccess(self, test):
        super(AMTestResult, self).addSuccess(test)
        self.runner.write("PASS: %s\n" % str(test))

    def addFailure(self, test, err):
        super(AMTestResult, self).addFailure(test, err)
        self.runner.write("FAIL: %s: %s\n" % (str(test), str(err[1])))

    def addSkip(self, test, reason):
        super(AMTestResult, self).addSkip(test, reason)
        self.runner.write("SKIP: %s: %s\n" % (str(test), str(reason)))

    def addExpectedFailure(self, test, err):
        super(AMTestResult, self).addExpectedFailure(test, err)
        self.runner.write("XFAIL: %s: %s\n" % (str(test), str(err[1])))

    def addUnexpectedSuccess(self, test):
        super(AMTestResult, self).addUnexpectedSuccess(test)
        self.runner.write("XPASS: %s\n" % str(test))

class AMTestRunner:
    """
    Test runner which prints output in automake "Simple tests" format. See
    http://www.gnu.org/software/automake/manual/automake.html#Simple-Tests
    for further details on this format.
    """

    def __init__(self, stream=sys.stderr, show_tracebacks=False):
        self.stream = stream
        self.show_tracebacks = show_tracebacks

    def write(self, message):
        self.stream.write(message)

    def run(self, test):
        result = AMTestResult(self)
        test(result)
        return result
