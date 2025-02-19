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

"""Utility methods/classes."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
import sys
from typing import Optional


class Error(Exception):
    pass


class ValueError(Error):

    msg: str

    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class UnimplementedError(Error):

    msg: str

    def __init__(self, msg):
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


def Warning(msg: str):
    sys.stderr.write('warning: %s\n' % msg)


class Transaction:

    desc: Optional[str] = None
    buyDate: Optional[datetime] = None
    buyDateStr: Optional[str] = None
    costBasis: Optional[Decimal] = None
    sellDate: Optional[datetime] = None
    sellDateStr: Optional[str] = None
    saleProceeds: Optional[Decimal] = None
    adjustment: Optional[Decimal] = None
    entryCode: Optional[int] = None

    def __str__(self) -> str:
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


def txfDate(date: datetime) -> str:
    """Returns a date string in the TXF format, which is MM/DD/YYYY."""
    return date.strftime('%m/%d/%Y')


def isLongTerm(buy_date: datetime, sell_date: datetime) -> bool:
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
