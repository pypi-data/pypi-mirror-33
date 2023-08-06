class CancelOrderRequest(object):
    def __init__(self, order_id: str):
        self.__order_id = order_id

    def order_id(self) -> str:
        return self.__order_id

    def to_json(self):
        return {
            'order_id': self.order_id()
        }
