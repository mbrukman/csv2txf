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

"""Utility methods/classes."""

import sys


class Error(Exception):
    pass


class ValueError(Error):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class UnimplementedError(Error):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def Warning(str):
    sys.stderr.write('warning: %s' % str)


class Transaction(object):
    def __init__(self):
        self.desc = None
        self.buyDateStr = None
        self.costBasis = None
        self.sellDateStr = None
        self.saleProceeds = None
        self.adjustment = None
        self.entryCode = None

    def __str__(self):
        data = [
            ('desc:%s', self.desc),
            ('buyDateStr:%s', self.buyDateStr),
            ('costBasis:%.2f', self.costBasis),
            ('sellDateStr:%s', self.sellDateStr),
            ('saleProceeds:%.2f', self.saleProceeds),
            ('adjustment:%.2f', self.adjustment),
            ('entryCode:%d', self.entryCode)
        ]
        formatted_data = [(fmt % value) for (fmt, value) in data if value]
        return ','.join(formatted_data)


def txfDate(date):
    """Returns a date string in the TXF format, which is MM/DD/YYYY."""
    return date.strftime('%m/%d/%Y')


def isLongTerm(buy_date, sell_date):
    # To handle leap years, cannot use a standard number of days, i.e.:
    #   sell_date - buy_date > timedelta(days=365)
    #   - doesn't work for leap years
    #   sell_date - buy_date > timedelta(days=366)
    #   - doesn't work for non-leap years
    if sell_date < buy_date:
        raise ValueError('Sell date before buy date')
    if sell_date.year > buy_date.year + 1:
        return True
    return (sell_date.year == buy_date.year + 1 and
            (sell_date.month > buy_date.month or
             (sell_date.month == buy_date.month and
              sell_date.day > buy_date.day)))
