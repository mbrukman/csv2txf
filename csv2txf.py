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

"""Converts a file to TXF for import into tax software.

Does not handle:
* dividends

Docs:
* TXF standard: http://turbotax.intuit.com/txf/
"""

from datetime import datetime
import sys
from utils import txfDate
from brokers import GetBroker


def ConvertTxnListToTxf(txn_list, tax_year):
    lines = []
    lines.append('V042')  # Version
    lines.append('Acsv2txf')  # Program name/version
    lines.append('D%s' % txfDate(datetime.today()))  # Export date
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


def RunConverter(broker_name, filename, tax_year):
    broker = GetBroker(broker_name, filename)
    txn_list = broker.parseFileToTxnList(filename, tax_year)
    return ConvertTxnListToTxf(txn_list, tax_year)


def main(argv):
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--broker", dest="broker", help="broker name")
    parser.add_option("-f", "--file", dest="filename", help="input file")
    parser.add_option("-o", "--outfile", dest="out_filename",
                      help="output file, leave empty for stdout")
    parser.add_option("--year", dest="year", help="tax year", type="int")
    (options, args) = parser.parse_args(argv)

    if not options.year:
        options.year = datetime.today().year - 1

    txf_lines = RunConverter(options.broker, options.filename, options.year)
    txf_out = '\n'.join(txf_lines)

    if options.out_filename:
        open(options.out_filename, 'w').write(txf_out)
    else:
        print(txf_out)


if __name__ == '__main__':
    main(sys.argv)
