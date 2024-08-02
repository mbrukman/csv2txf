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

"""Implements InteractiveBrokers.

Does not handle:
* dividends
"""

import csv
from datetime import datetime
from decimal import Decimal
import utils


FIRST_LINE = 'Title,Worksheet for Form 8949,'


class InteractiveBrokers:
    @classmethod
    def name(cls):
        return 'Interactive Brokers'

    @classmethod
    def DetermineEntryCode(cls, part, box):
        if part == 1:
            if box == 'A':
                return 321
            elif box == 'B':
                return 711
            elif box == 'C':
                return 712
        elif part == 2:
            if box == 'A':
                return 323
            elif box == 'B':
                return 713
            elif box == 'C':
                return 714
        return None

    @classmethod
    def TryParseYear(cls, date_str):
        try:
            return datetime.strptime(date_str, '%m/%d/%Y').year
        except ValueError:
            return None

    @classmethod
    def ParseDollarValue(cls, value):
        return Decimal(value.replace(',', '').replace('"', ''))

    @classmethod
    def isFileForBroker(cls, filename):
        with open(filename) as f:
            first_line = f.readline()
            return first_line.find(FIRST_LINE) == 0

    @classmethod
    def parseFileToTxnList(cls, filename, tax_year):
        with open(filename) as f:
            # First 2 lines are headers.
            f.readline()
            f.readline()
            txns = csv.reader(f, delimiter=',', quotechar='"')

            txn_list = []
            part = None
            box = None
            entry_code = None

            for row in txns:
                if row[0] == 'Part' and len(row) == 3:
                    box = None
                    if row[1] == 'I':
                        part = 1
                    elif row[1] == 'II':
                        part = 2
                    else:
                        utils.Warning('unknown part line: "%s"\n' % row)
                elif row[0] == 'Box' and len(row) == 3:
                    if row[1] == 'A' or row[1] == 'B' or row[1] == 'C':
                        box = row[1]
                        entry_code = cls.DetermineEntryCode(part, box)
                    else:
                        utils.Warning('unknown box line: "%s"\n' % row)
                elif row[0] == 'Data' and len(row) == 9:
                    if not entry_code:
                        utils.Warning(
                            'ignoring data: "%s" as the code is not defined\n')
                        continue
                    txn = utils.Transaction()
                    txn.desc = row[1]
                    txn.buyDateStr = row[3]
                    txn.sellDateStr = row[4]
                    year = cls.TryParseYear(txn.sellDateStr)
                    txn.saleProceeds = cls.ParseDollarValue(row[5])
                    txn.costBasis = cls.ParseDollarValue(row[6])
                    if row[7]:
                        txn.adjustment = cls.ParseDollarValue(row[7])
                    txn.entryCode = entry_code
                    if tax_year and year and year != tax_year:
                        utils.Warning('ignoring txn: "%s" as the sale is not from %d\n' %
                                      (txn.desc, tax_year))
                    else:
                        txn_list.append(txn)
                    txn = None
                elif (row[0] != 'Header' and row[0] != 'Footer') or len(row) != 9:
                    utils.Warning('unknown line: "%s"\n' % row)

            return txn_list
