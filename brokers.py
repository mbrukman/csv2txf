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

"""Code for figuring out which broker to use.

To define a new broker:
1) Create a new class and define the following method:
  @classmethod
  def parseFileToTxnList(cls, filename, tax_year):
    Note that if tax_year == None, then all transactions should be accepted.
2) If there is an easy way to determine if a particular file is usable
   by your class, then define the method:
  @classmethod
  def isFileForBroker(cls, filename):
    Note that if this method is not defined, then you may need to modify
    update_testdata.py as well.
3) Add your class to the BROKERS map below.
"""

from __future__ import annotations

from typing import Optional, Type

from broker import Broker
from interactive_brokers import InteractiveBrokers
from tdameritrade import TDAmeritrade
from vanguard import Vanguard
from schwab import Schwab


BROKERS: dict[str, Type[Broker]] = {
    'amtd': TDAmeritrade,
    'ib': InteractiveBrokers,
    'tdameritrade': TDAmeritrade,
    'vanguard': Vanguard,
    'schwab' : Schwab
}


def DetectBroker(filename: str) -> Optional[Type[Broker]]:
    for (broker_name, broker) in BROKERS.items():
        if hasattr(broker, 'isFileForBroker'):
            if broker.isFileForBroker(filename):
                return broker

    return None


def GetBroker(broker_name: str, filename: str) -> Type[Broker]:
    if broker_name in BROKERS:
        return BROKERS[broker_name]

    broker: Optional[Type[Broker]] = DetectBroker(filename)
    if not broker:
        raise Exception('Invalid broker name: %s' % broker_name)

    return broker
