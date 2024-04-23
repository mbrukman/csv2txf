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

"""Converts a file to TXF for import into tax software.

Does not handle:
* dividends

Docs:
* TXF standard: http://turbotax.intuit.com/txf/
"""

from __future__ import annotations

from decimal import Decimal
from datetime import datetime
import sys
from typing import List

from brokers import GetBroker
import utils


def ConvertTxnListToTxf(txn_list: list[utils.Transaction], tax_year: int, date: str) -> List[str]:
    lines = []
    lines.append('V042')  # Version
    lines.append('Acsv2txf')  # Program name/version
    if date is None:
        date = utils.txfDate(datetime.today())
    lines.append('D%s' % date)  # Export date
    lines.append('^')
    for txn in txn_list:
        lines.append('TD')
        lines.append('N%d' % txn.entryCode)
        lines.append('C1')
        lines.append('L1')
        lines.append('P%s' % txn.desc)
        lines.append('D%s' % txn.buyDateStr)
        lines.append('D%s' % txn.sellDateStr)
        lines.append('$%.2f' % txn.costBasis)
        lines.append('$%.2f' % txn.saleProceeds)
        if txn.adjustment:
            lines.append('$%.2f' % txn.adjustment)
        lines.append('^')
    return lines


def RunConverter(broker_name: str, filename: str, tax_year: int, date: str) -> List[str]:
    broker = GetBroker(broker_name, filename)
    txn_list = broker.parseFileToTxnList(filename, tax_year)
    return ConvertTxnListToTxf(txn_list, tax_year, date)


def GetSummary(broker_name: str, filename: str, tax_year: int) -> str:
    broker = GetBroker(broker_name, filename)
    total_cost = Decimal(0)
    total_sales = Decimal(0)
    txn_list = broker.parseFileToTxnList(filename, tax_year)
    for txn in txn_list:
        assert txn.costBasis is not None
        total_cost += txn.costBasis
        assert txn.saleProceeds is not None
        total_sales += txn.saleProceeds

    return '\n'.join([
        '%s summary report for %d' % (broker.name(), tax_year),
        'Num sale txns:  %d' % len(txn_list),
        'Total cost:     $%.2f' % total_cost,
        'Total proceeds: $%.2f' % total_sales,
        'Net gain/loss:  $%.2f' % (total_sales - total_cost),
    ])

def main(argv):
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--broker", dest="broker", help="broker name or alias")
    parser.add_option("-f", "--file", dest="filename", help="input file")
    parser.add_option("-o", "--outfile", dest="out_filename",
                      help="output file, leave empty for stdout")
    parser.add_option("--outfmt", dest="out_format",
                      help="output format: `txf` or `summary`")
    parser.add_option("--year", dest="year", help="tax year", type="int")
    parser.add_option("--date", dest="date", help="date to output", type="str")
    (options, args) = parser.parse_args(argv)

    if not options.filename:
        sys.stderr.write('Filename is required; specify with `--file` flag.\n')
        sys.exit(1)

    if options.year:
        year = int(options.year)
    else:
        year = datetime.today().year - 1
        utils.Warning(f'Year not specified, defaulting to {year} (last year)\n')

    output = None
    if options.out_format == 'summary':
        output = GetSummary(options.broker, options.filename, year)
    else:
        txf_lines = RunConverter(options.broker, options.filename, year, options.date)
        output = '\n'.join(txf_lines)

    if options.out_filename:
        with open(options.out_filename, 'w') as out:
            out.write(output)
    else:
        print(output)


if __name__ == '__main__':
    main(sys.argv)
