import json
from typing import Sequence, Mapping
from .order import Order


class Account(object):
    def __init__(self, sequence_number: int, orders: Sequence[Order], balance: Mapping[str, float]):
        self.__sequence_number = sequence_number
        self.__orders = orders
        self.__balance = balance

    def sequence_number(self) -> int:
        return self.__sequence_number

    def orders(self) -> Sequence[Order]:
        return self.__orders

    def balance(self) -> Mapping[str, float]:
        return self.__balance

    @staticmethod
    def from_json(data):
        return Account(int(data['sequence_number']),
                       [Order.from_json(order_data) for order_data in data['orders']],
                       dict([(k, v) for k, v in data['balance'].items()]))

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
