#!/usr/bin/python
#
# Copyright 2012 Google LLC
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

import glob
import os
import unittest
from interactive_brokers import InteractiveBrokers


class InteractiveBrokersTest(unittest.TestCase):
    def testDetect(self):
        for csv in glob.glob('testdata/*.csv'):
            self.assertEqual(os.path.basename(csv) == 'interactive_brokers.csv',
                             InteractiveBrokers.isFileForBroker(csv))

    def testParse(self):
        data = InteractiveBrokers.parseFileToTxnList(
            'testdata/interactive_brokers.csv', 2011)
        with open('testdata/interactive_brokers.parse') as expected_file:
            for txn in data:
                expected_txn = expected_file.readline().strip()
                self.assertEqual(expected_txn, str(txn))


if __name__ == '__main__':
    unittest.main()
