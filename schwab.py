#!/usr/bin/python
#
# Copyright 2021 Chetan Narsude <chetan+csv2txf@celeral.com>
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

"""Implements Schwab

Charles Schwab gain/loss output provides already-reconciled transactions, i.e.,
each buy/sell pair comes in a single record, on a single line.

Does not handle:
* dividends
* short sales
* partial lot sales
"""

import csv
from datetime import datetime
from decimal import Decimal
import re
import utils


FIRST_LINE = 'Description of property (Example 100 sh. XYZ Co.),Date acquired,Date sold or disposed,Proceeds,Cost or other basis,Accrued market discount,Wash sale loss disallowed,Short-Term gain loss Long-term gain or loss Ordinary,Form 8949 Code,Check if proceeds from collectibles QOF,Federal income tax withheld,Check if noncovered security,Reported to IRS: Gross proceeds Net proceeds,Check if loss is not allowed based on amount in 1d,Profit or (loss) realized in 2020 on closed contracts,Unrealized profit or (loss) on open contracts-12/31/2019,Unrealized profit or (loss) on open contracts-12/31/2020,Aggregate profit or (loss) on contracts,Check if basis reported to IRS,Bartering,State name,State identification no,State Tax Withheld\n'

TRANSACTION_TYPE = 'Trans type'


class Schwab:
    @classmethod
    def name(cls):
        return "Charles Schwab"

    @classmethod
    def washSaleDisallowedAmount(cls, dict):
        """Returns wash sale disallowed amount"""
        value = dict['Wash sale loss disallowed'].rstrip()
        if value == '$0.00':
            return None
        else:
            return Decimal(value.replace(',', '').replace('$', ''))

    @classmethod
    def buyDate(cls, dict):
        """Returns date of transaction as datetime object."""
        # Our input date format is MM/DD/YYYY.
        if  dict['Date acquired'] == 'Various':
            return dict['Date acquired']
        else:
            return datetime.strptime(dict['Date acquired'], '%m/%d/%Y')

    @classmethod
    def sellDate(cls, dict):
        """Returns date of transaction as datetime object."""
        # Our input date format is MM/DD/YYYY.
        if dict['Date sold or disposed'] == 'Various':
            return dict['Date sold or disposed']
        else:
            return datetime.strptime(dict['Date sold or disposed'], '%m/%d/%Y')

    @classmethod
    def isShortTerm(cls, dict):
        return dict['Short-Term gain loss Long-term gain or loss Ordinary'] == 'Short Term'

    @classmethod
    def symbol(cls, dict):
        return dict['Description of property (Example 100 sh. XYZ Co.)']

    @classmethod
    def numShares(cls, dict):
        match = re.match('^([^ ]*) ', dict['Description of property (Example 100 sh. XYZ Co.)'])
        if match:
            return Decimal(match.group(1))
        else:
            raise Exception('num shares could not be fund in %s' % dict)

    @classmethod
    def costBasis(cls, dict):
        # Proceeds amount may include commas as thousand separators, which
        # Decimal does not handle.
        return Decimal(dict['Cost or other basis'].replace(',', ''))

    @classmethod
    def saleProceeds(cls, dict):
        # Proceeds amount may include commas as thousand separators, which
        # Decimal does not handle.
        return Decimal(dict['Proceeds'].replace(',', ''))

    @classmethod
    def isFileForBroker(cls, filename):
        with open(filename) as f:
            first_line = f.readline()
            return first_line == FIRST_LINE

    @classmethod
    def parseFileToTxnList(cls, filename, tax_year):
        buy_date = datetime.strptime('01/02/2020', '%m/%d/%Y')
        sell_date = datetime.strptime('12/30/2020', '%m/%d/%Y')
        txns = csv.reader(open(filename), delimiter=',', quotechar='"')
        line_num = 0
        txn_list = []
        names = None
        for row in txns:
            line_num = line_num + 1
            if line_num == 1:
                names = row
                continue

            txn_dict = {}
            for i in range(0, len(names)):
                txn_dict[names[i]] = row[i]

            if txn_dict['Description of property (Example 100 sh. XYZ Co.)'] == '':
                # This is the summary line where the string 'Total:' appears in
                # the first column, so we're done.
                break

            adjustment = cls.washSaleDisallowedAmount(txn_dict)
            if not adjustment:
                continue

            curr_txn = utils.Transaction()
            curr_txn.adjustment = adjustment
            
            #curr_txn.desc = '%s shares %s' % (
            #    cls.numShares(txn_dict), cls.symbol(txn_dict))
            curr_txn.desc = cls.symbol(txn_dict)
            curr_txn.buyDate = cls.buyDate(txn_dict)
            if curr_txn.buyDate == 'Various':
                curr_txn.buyDate = buy_date
                curr_txn.buyDateStr = 'Various'
            else:
                curr_txn.buyDateStr = utils.txfDate(curr_txn.buyDate)

            curr_txn.costBasis = cls.costBasis(txn_dict)
            curr_txn.sellDate = cls.sellDate(txn_dict)
            if curr_txn.sellDate == 'Various':
                curr_txn.sellDate = sell_date
                curr_txn.sellDateStr = 'Various'
            else:
                curr_txn.sellDateStr = utils.txfDate(curr_txn.sellDate)

            curr_txn.saleProceeds = cls.saleProceeds(txn_dict)

            #assert curr_txn.sellDate >= curr_txn.buyDate
            if cls.isShortTerm(txn_dict):
                # TODO(mbrukman): assert here that (sellDate - buyDate) <= 1 year
                if adjustment:
                    curr_txn.entryCode = 682
                else:
                    curr_txn.entryCode = 321  # "ST gain/loss - security"
            else:
                # TODO(mbrukman): assert here that (sellDate - buyDate) > 1 year
                curr_txn.entryCode = 323  # "LT gain/loss - security"

            if tax_year and curr_txn.sellDate.year != tax_year:
                utils.Warning('ignoring txn: "%s" (line %d) as the sale is not from %d\n' %
                              (curr_txn.desc, line_num, tax_year))
                continue

            txn_list.append(curr_txn)

        return txn_list
