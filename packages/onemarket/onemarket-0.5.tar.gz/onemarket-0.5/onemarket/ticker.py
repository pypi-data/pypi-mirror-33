import json
from . import AssetPair


class Ticker(object):
    def __init__(self, exchange: str, pair: AssetPair, timestamp: int, bid: float, bid_volume: float,
                 ask: float, ask_volume: float):
        self.__exchange = exchange
        self.__pair = pair
        self.__timestamp = timestamp
        self.__bid = bid
        self.__bid_volume = bid_volume
        self.__ask = ask
        self.__ask_volume = ask_volume

    def exchange(self) -> str:
        return self.__exchange

    def pair(self) -> AssetPair:
        return self.__pair

    def timestamp(self) -> int:
        return self.__timestamp

    def bid(self) -> float:
        return self.__bid

    def bid_volume(self) -> float:
        return self.__bid_volume

    def ask(self) -> float:
        return self.__ask

    def ask_volume(self) -> float:
        return self.__ask_volume

    def mid(self) -> float:
        return (self.bid() + self.ask())/2

    def spread(self) -> float:
        return self.ask()-self.bid()

    @staticmethod
    def from_json(data):
        return Ticker(data['exchange'], AssetPair.from_json(data['pair']), data['timestamp'], data['bid'],
                      data['bid_volume'], data['ask'], data['ask_volume'])

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)
