#
# Example code using the AMTestRunner class
#
# Copyright (c) 2018 Beta Five Ltd
#
# SPDX-License-Identifier: Apache-2.0
#

import unittest

from betatest.amtest import AMTestRunner

class AMTestExample(unittest.TestCase):
    def test_pass(self):
        pass
    
    def test_fail(self):
        self.fail('Unexpected failure')
    
    @unittest.skip('Skipped')
    def test_skip(self):
        pass
    
    @unittest.expectedFailure
    def test_xfail(self):
        self.fail('Expected failure')
    
    @unittest.expectedFailure
    def test_xpass(self):
        pass
    
    def test_error(self):
        return 1.0 / 0.0

if __name__ == '__main__':
    unittest.main(testRunner=AMTestRunner)
