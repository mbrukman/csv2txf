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

"""Updates the testdata/*.golden files for various brokers.

Re-generates the transactions for each broker and writes them out as ASCII
strings.
"""

import glob
import os
import sys

from brokers import DetectBroker

# If your broker parser does not support isFileForBroker, you'll need
# need to add an entry here.
# Example:
# 'vanguard.csv' : Vanguard
BROKER_CSV = {}


def main(argv):
    for csv in glob.glob('testdata/*.csv'):
        (path, filename) = os.path.split(csv)
        if filename in BROKER_CSV:
            broker = BROKER_CSV[filename]
        else:
            broker = DetectBroker(csv)
        if not broker:
            continue

        golden = csv.replace('.csv', '.parse')
        if not os.access(path, os.W_OK) or (not os.access(golden, os.W_OK) and
                                            os.path.exists(golden)):
            sys.stderr.write('error: %s is not writeable\n' % golden)
            sys.exit(1)

        with open(golden, 'w') as out:
            data = broker.parseFileToTxnList(csv, None)
            for txn in data:
                out.write('%s\n' % str(txn))
            print("Generated: %s from %s" % (golden, csv))


if __name__ == '__main__':
    main(sys.argv)
