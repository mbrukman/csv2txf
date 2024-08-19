# Copyright 2020 Google LLC
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

"""Implements TD Ameritrade.

TD Ameritrade gain/loss output provides already-reconciled transactions, i.e.,
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


FIRST_LINE = ','.join([
    'Security', 'Trans type', 'Qty', 'Open date', 'Adj cost',
    'Close date', 'Adj proceeds', 'Adj gain($)', 'Adj gain(%)',
    'Term\n'])

TRANSACTION_TYPE = 'Trans type'


class TDAmeritrade:
    @classmethod
    def name(cls):
        return "TD Ameritrade"

    @classmethod
    def buyDate(cls, dict):
        """Returns date of transaction as datetime object."""
        # Our input date format is MM/DD/YYYY.
        return datetime.strptime(dict['Open date'], '%m/%d/%Y')

    @classmethod
    def sellDate(cls, dict):
        """Returns date of transaction as datetime object."""
        # Our input date format is MM/DD/YYYY.
        return datetime.strptime(dict['Close date'], '%m/%d/%Y')

    @classmethod
    def isShortTerm(cls, dict):
        return dict['Term'] == 'Short-term'

    @classmethod
    def symbol(cls, dict):
        match = re.match('^.*\((.*)\)$', dict['Security'])
        if match:
            return match.group(1)
        else:
            raise Exception('Security symbol not found in: %s' % dict)

    @classmethod
    def numShares(cls, dict):
        return Decimal(dict['Qty'])

    @classmethod
    def costBasis(cls, dict):
        # Proceeds amount may include commas as thousand separators, which
        # Decimal does not handle.
        return Decimal(dict['Adj cost'].replace(',', ''))

    @classmethod
    def saleProceeds(cls, dict):
        # Proceeds amount may include commas as thousand separators, which
        # Decimal does not handle.
        return Decimal(dict['Adj proceeds'].replace(',', ''))

    @classmethod
    def isFileForBroker(cls, filename):
        with open(filename) as f:
            first_line = f.readline()
            return first_line == FIRST_LINE

    @classmethod
    def parseFileToTxnList(cls, filename, tax_year):
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

            if txn_dict['Security'] == 'Total:':
                # This is the summary line where the string 'Total:' appears in
                # the first column, so we're done.
                break

            curr_txn = utils.Transaction()
            curr_txn.desc = '%s shares %s' % (
                cls.numShares(txn_dict), cls.symbol(txn_dict))
            curr_txn.buyDate = cls.buyDate(txn_dict)
            curr_txn.buyDateStr = utils.txfDate(curr_txn.buyDate)
            curr_txn.costBasis = cls.costBasis(txn_dict)
            curr_txn.sellDate = cls.sellDate(txn_dict)
            curr_txn.sellDateStr = utils.txfDate(curr_txn.sellDate)
            curr_txn.saleProceeds = cls.saleProceeds(txn_dict)

            assert curr_txn.sellDate >= curr_txn.buyDate
            if cls.isShortTerm(txn_dict):
                # TODO(mbrukman): assert here that (sellDate - buyDate) <= 1 year
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
