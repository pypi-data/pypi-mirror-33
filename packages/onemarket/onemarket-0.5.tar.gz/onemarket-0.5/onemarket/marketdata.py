import json
from typing import Sequence
from .account import Account
from .ticker import Ticker


class MarketData(object):
    def __init__(self, account: Account, market: Sequence[Ticker]):
        self.__account = account
        self.__market = market

    def account(self):
        return self.__account

    def market(self):
        return self.__market

    @staticmethod
    def from_json(data):
        return MarketData(Account.from_json(data['account']),
                          [Ticker.from_json(ticker_json) for ticker_json in data['market']])
