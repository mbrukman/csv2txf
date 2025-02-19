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

from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal
from typing import Optional

from broker import Broker
from typing_extensions import override
import utils


FIRST_LINE = ','.join(['"Trade Date"', '"Transaction Type"',
                       '"Investment Name"', '"Symbol"', '"Shares"',
                       '"Principal Amount"', '"Net Amount"\n'])


class Vanguard(Broker):

    @classmethod
    @override
    def name(cls) -> str:
        return 'Vanguard'

    @classmethod
    def isBuy(cls, txn: dict[str, str]) -> bool:
        return txn['Transaction Type'] == 'Buy'

    @classmethod
    def isSell(cls, txn: dict[str, str]) -> bool:
        return txn['Transaction Type'] == 'Sell'

    @classmethod
    def date(cls, txn: dict[str, str]) -> datetime:
        """Returns date of transaction as datetime object."""
        # Our input date format is YYYY/MM/DD.
        return datetime.strptime(txn['Trade Date'], '%Y-%m-%d')

    @classmethod
    def symbol(cls, txn: dict[str, str]) -> str:
        return txn['Symbol']

    @classmethod
    def investmentName(cls, txn: dict[str, str]) -> str:
        return txn['Investment Name']

    @classmethod
    def numShares(cls, txn: dict[str, str]) -> int:
        shares = int(txn['Shares'])
        if cls.isSell(txn):
            return shares * -1
        else:
            return shares

    @classmethod
    def netAmount(cls, txn: dict[str, str]) -> Decimal:
        amount = Decimal(txn['Net Amount'])
        if cls.isBuy(txn):
            return amount * -1
        else:
            return amount

    @classmethod
    @override
    def isFileForBroker(cls, filename: str) -> bool:
        with open(filename) as f:
            first_line = f.readline()
            return first_line == FIRST_LINE

    @classmethod
    @override
    def parseFileToTxnList(cls, filename: str, tax_year: Optional[int]) -> list[utils.Transaction]:
        txns = csv.reader(open(filename), delimiter=',', quotechar='"')
        row_num: int = 0
        txn_list: list[utils.Transaction] = []
        names: list[str] = []
        curr_txn: Optional[utils.Transaction] = None
        buy: dict[str, str] = {}
        sell: dict[str, str] = {}
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
                assert curr_txn is not None
                assert cls.numShares(buy) == cls.numShares(sell)
                assert cls.symbol(buy) == cls.symbol(sell)
                assert cls.investmentName(buy) == cls.investmentName(sell)

                buyDate: Optional[datetime] = curr_txn.buyDate
                if buyDate is None:
                    utils.Warning(f'Missing buy date for current transaction: {curr_txn}')
                    continue

                sellDate: datetime = cls.date(sell)
                curr_txn.sellDateStr = utils.txfDate(sellDate)
                curr_txn.saleProceeds = cls.netAmount(sell)

                if utils.isLongTerm(buyDate, sellDate):
                    curr_txn.entryCode = 323  # "LT gain/loss - security"
                else:
                    curr_txn.entryCode = 321  # "ST gain/loss - security"

                assert sellDate >= buyDate, f'Sell date ({sellDate}) must be on or after buy date ({buyDate})'
                if tax_year and sellDate.year != tax_year:
                    utils.Warning('ignoring txn: "%s" as the sale is not from %d' %
                                  (curr_txn.desc, tax_year))
                    continue

                txn_list.append(curr_txn)

                # Clear both the buy and the sell as we have matched them up.
                buy = {}
                sell = {}
                curr_txn = None

        return txn_list
