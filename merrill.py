# Copyright 2026 Melabela <43100514+Melabela@users.noreply.github.com>
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

"""Implements Merrill.

Merrill gain/loss output provides already-reconciled transactions, i.e.,
each buy/sell pair comes in a single record, on a single line.

Does not handle:
* dividends
* short sales
* partial lot sales
"""

from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal
import re
from typing import Optional

from broker import Broker
from typing_extensions import override
import utils


# CSV headings are quoted (")
FIRST_LINE = ','.join([
    '"Transactions"',
    '"Quantity"',
    '"Description of Property"',
    '"Cusip"',
    '"Date of Acquisition"',
    '"Date of Sale or Exchange"',
    '"Sales Price (see Schedule D instructions)"',
    '"Cost Basis"',
    '"Accrued Market Discount"',
    '"Wash Sale Loss Disallowed"',
    '"Gain or (Loss)"',
    '"Transaction Description"',
    '"YTD Amortization/Accretion"',
    '"LTD Amortization/Accretion"',
    '"Proceeds from Collectibles"\n'
])


#TRANSACTION_TYPE = 'Transaction Description'


class Merrill(Broker):

    @classmethod
    @override
    def name(cls) -> str:
        return "Merrill"

    @classmethod
    def buyDate(cls, txn: dict[str, str]) -> datetime:
        """Returns date of transaction as datetime object."""
        # Our input date format is MM/DD/YY.
        return datetime.strptime(txn['Date of Acquisition'], '%m/%d/%y')

    @classmethod
    def sellDate(cls, txn: dict[str, str]) -> datetime:
        """Returns date of transaction as datetime object."""
        # Our input date format is MM/DD/YY.
        return datetime.strptime(txn['Date of Sale or Exchange'], '%m/%d/%y')

    @classmethod
    def isShortTerm(cls, txn: dict[str, str]) -> bool:
        return txn['Transactions'].startswith("SHORT TERM")

    @classmethod
    def symbol(cls, txn: dict[str, str]) -> str:
        # No symbol provided in CSV data, just get full company name
        return txn['Description of Property']

    @classmethod
    def numShares(cls, txn: dict[str, str]) -> Decimal:
        return Decimal(txn['Quantity'])

    @classmethod
    def costBasis(cls, txn: dict[str, str]) -> Decimal:
        # Proceeds amount may include commas as thousand separators, which
        # Decimal does not handle.
        return Decimal(txn['Cost Basis'].replace(',', ''))

    @classmethod
    def saleProceeds(cls, txn: dict[str, str]) -> Decimal:
        # Proceeds amount may include commas as thousand separators, which
        # Decimal does not handle.
        return Decimal(txn['Sales Price (see Schedule D instructions)'].replace(',', ''))

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
        line_num = 0
        txn_list: list[utils.Transaction] = []
        names: list[str] = []
        for row in txns:
            line_num = line_num + 1
            if line_num == 1:
                names = row
                continue

            txn_dict = {}
            for i in range(0, len(names)):
                txn_dict[names[i]] = row[i]

            curr_txn = utils.Transaction()
            curr_txn.desc = '%s shares %s' % (
                cls.numShares(txn_dict), cls.symbol(txn_dict))
            buyDate = cls.buyDate(txn_dict)
            curr_txn.buyDateStr = utils.txf_date(buyDate)
            curr_txn.costBasis = cls.costBasis(txn_dict)
            sellDate = cls.sellDate(txn_dict)
            curr_txn.sellDateStr = utils.txf_date(sellDate)
            curr_txn.saleProceeds = cls.saleProceeds(txn_dict)

            assert sellDate >= buyDate, f'Sell date ({sellDate}) must be on or after buy date ({buyDate})'
            if cls.isShortTerm(txn_dict):
                # TODO(mbrukman): assert here that (sellDate - buyDate) <= 1 year
                curr_txn.entryCode = 321  # "ST gain/loss - security"
            else:
                # TODO(mbrukman): assert here that (sellDate - buyDate) > 1 year
                curr_txn.entryCode = 323  # "LT gain/loss - security"

            if tax_year and sellDate.year != tax_year:
                utils.warn('ignoring txn: "%s" (line %d) as the sale is not from %d' %
                           (curr_txn.desc, line_num, tax_year))
                continue

            txn_list.append(curr_txn)

        return txn_list
