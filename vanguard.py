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

"""Implements Vanguard.

Assumes reconciled transactions, i.e., sell follows buy.

Does not handle:
* dividends
* short sales
* partial lot sales
"""

import csv
from datetime import datetime
from decimal import Decimal
import utils


FIRST_LINE = ','.join(['"Trade Date"', '"Transaction Type"',
                       '"Investment Name"', '"Symbol"', '"Shares"',
                       '"Principal Amount"', '"Net Amount"\n'])


class Vanguard:
    @classmethod
    def isBuy(cls, dict):
        return dict['Transaction Type'] == 'Buy'

    @classmethod
    def isSell(cls, dict):
        return dict['Transaction Type'] == 'Sell'

    @classmethod
    def date(cls, dict):
        """Returns date of transaction as datetime object."""
        # Our input date format is YYYY/MM/DD.
        return datetime.strptime(dict['Trade Date'], '%Y-%m-%d')

    @classmethod
    def symbol(cls, dict):
        return dict['Symbol']

    @classmethod
    def name(cls, dict):
        return dict['Investment Name']

    @classmethod
    def numShares(cls, dict):
        shares = int(dict['Shares'])
        if cls.isSell(dict):
            return shares * -1
        else:
            return shares

    @classmethod
    def netAmount(cls, dict):
        amount = Decimal(dict['Net Amount'])
        if cls.isBuy(dict):
            return amount * -1
        else:
            return amount

    @classmethod
    def isFileForBroker(cls, filename):
        with open(filename) as f:
            first_line = f.readline()
            return first_line == FIRST_LINE

    @classmethod
    def parseFileToTxnList(cls, filename, tax_year):
        txns = csv.reader(open(filename), delimiter=',', quotechar='"')
        row_num = 0
        txn_list = []
        names = None
        curr_txn = None
        buy = None
        sell = None
        for row in txns:
            row_num = row_num + 1
            if row_num == 1:
                names = row
                continue

            txn_dict = {}
            for i in range(0, len(names)):
                txn_dict[names[i]] = row[i]

            if cls.isBuy(txn_dict):
                buy = txn_dict
                curr_txn = utils.Transaction()
                curr_txn.desc = '%d shares %s' % (
                    cls.numShares(buy), cls.symbol(buy))
                curr_txn.buyDate = cls.date(txn_dict)
                curr_txn.buyDateStr = utils.txfDate(curr_txn.buyDate)
                curr_txn.costBasis = cls.netAmount(txn_dict)
            elif cls.isSell(txn_dict):
                sell = txn_dict
                # Assume that sells follow the buys, so we can attach this sale to the
                # current buy txn we are processing.
                assert cls.numShares(buy) == cls.numShares(sell)
                assert cls.symbol(buy) == cls.symbol(sell)
                assert cls.name(buy) == cls.name(sell)

                curr_txn.sellDate = cls.date(sell)
                curr_txn.sellDateStr = utils.txfDate(curr_txn.sellDate)
                curr_txn.saleProceeds = cls.netAmount(sell)

                if utils.isLongTerm(curr_txn.buyDate, curr_txn.sellDate):
                    curr_txn.entryCode = 323  # "LT gain/loss - security"
                else:
                    curr_txn.entryCode = 321  # "ST gain/loss - security"

                assert curr_txn.sellDate >= curr_txn.buyDate
                if tax_year and curr_txn.sellDate.year != tax_year:
                    utils.Warning('ignoring txn: "%s" as the sale is not from %d\n' %
                                  (curr_txn.desc, tax_year))
                    continue

                txn_list.append(curr_txn)

                # Clear both the buy and the sell as we have matched them up.
                buy = None
                sell = None
                curr_txn = None

        return txn_list
