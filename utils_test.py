#!/usr/bin/python
#
# Copyright 2012 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for utils module."""

__author__ = 'mbrukman@google.com (Misha Brukman)'

from datetime import datetime
import unittest
import utils


class UtilsTest(unittest.TestCase):
    def testIsLongTermNonLeapYear(self):
        buy = datetime(2010, 1, 4)
        sell = datetime(2011, 1, 5)
        self.assertTrue(utils.isLongTerm(buy, sell))

    def testIsLongTermLeapYear(self):
        buy = datetime(2008, 1, 4)
        sell = datetime(2009, 1, 4)
        self.assertFalse(utils.isLongTerm(buy, sell))

    def testIsLongTermCorrectOrder(self):
        buy = datetime(2005, 1, 1)
        sell = datetime(2000, 1, 4)
        # TODO: verify error message.
        self.assertRaises(utils.ValueError, utils.isLongTerm, buy, sell)


if __name__ == '__main__':
    unittest.main()
