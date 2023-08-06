import json
from .assetpair import AssetPair


class AssetPairProperties(object):
    def __init__(self, pair: AssetPair, exchange_specific_id: str, price_significant_digits: int,
                 size_significant_digits: int, max_size: float):
        self.__pair = pair
        self.__exchange_specific_id = exchange_specific_id
        self.__price_significant_digits = price_significant_digits
        self.__size_significant_digits = size_significant_digits
        self.__max_size = max_size

    def pair(self) -> AssetPair:
        return self.__pair

    def exchange_specific_id(self) -> str:
        return self.__exchange_specific_id

    def price_significant_digits(self) -> int:
        return self.__price_significant_digits

    def size_significant_digits(self) -> int:
        return self.__size_significant_digits

    def max_size(self) -> float:
        return self.__max_size

    @staticmethod
    def from_json(data):
        return AssetPairProperties(AssetPair.from_json(data['pair']), data['exchange_specific_id'],
                                   data['price_significant_digits'], data['size_significant_digits'], data['max_size'])

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__)
