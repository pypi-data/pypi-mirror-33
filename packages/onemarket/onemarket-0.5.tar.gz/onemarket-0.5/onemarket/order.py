from .assetpair import AssetPair


class Order(object):
    def __init__(self, exchange: str, id: str, pair: AssetPair, side: str, price: float,
                 volume: float, expire_at: int, state: str):
        self.__exchange = exchange
        self.__id = id
        self.__pair = pair
        self.__side = side
        self.__price = price
        self.__volume = volume
        self.__expire_at = expire_at
        self.__state = state

    def exchange(self) -> str:
        return self.__exchange

    def id(self) -> str:
        return self.__id

    def pair(self) -> AssetPair:
        return self.__pair

    def side(self) -> str:
        return self.__side

    def price(self) -> float:
        return self.__price

    def volume(self) -> float:
        return self.__volume

    def expire_at(self) -> int:
        return self.__expire_at

    def state(self):
        return self.__state

    @staticmethod
    def from_json(data):
        return Order(data['exchange'], data['id'], AssetPair.from_json(data['pair']), data['side'],
                     data['price'], data['volume'], None, data['state'])
