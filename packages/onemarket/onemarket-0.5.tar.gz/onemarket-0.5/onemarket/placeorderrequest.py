import json
from .assetpair import AssetPair


class PlaceOrderRequest(object):
    def __init__(self, pair: AssetPair, price: float, volume: float, side: str):
        self.__pair = pair
        self.__price = price
        self.__volume = volume
        self.__side = side

    def pair(self) -> AssetPair:
        return self.__pair

    def price(self) -> float:
        return self.__price

    def volume(self) -> float:
        return self.__volume

    def side(self) -> str:
        return self.__side

    def to_json(self):
        return {
            'pair': self.pair().to_json(),
            'price': self.price(),
            'volume': self.volume(),
            'side': self.side()
        }

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(tuple(sorted(self.__dict__.items())))
