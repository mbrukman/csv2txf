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

"""Tests for interactive_brokers module."""

from datetime import datetime
import os
import unittest
from interactive_brokers import InteractiveBrokers


class InteractiveBrokersTest(unittest.TestCase):
    def testDetect(self):
        for dirname, dirnames, filenames in os.walk('testdata/'):
            for filename in filenames:
                if filename == 'interactive_brokers.csv':
                    self.assertTrue(InteractiveBrokers.isFileForBroker(
                        'testdata/interactive_brokers.csv'))
                else:
                    self.assertFalse(InteractiveBrokers.isFileForBroker(
                        'testdata/' + filename))

    def testParse(self):
        data = InteractiveBrokers.parseFileToTxnList(
            'testdata/interactive_brokers.csv', 2011)
        with open('testdata/interactive_brokers.golden') as expected_file:
            for txn in data:
                expected_txn = expected_file.readline().strip()
                self.assertEqual(expected_txn, str(txn))


if __name__ == '__main__':
    unittest.main()
