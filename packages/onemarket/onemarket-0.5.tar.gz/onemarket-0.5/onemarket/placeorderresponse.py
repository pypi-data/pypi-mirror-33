class PlaceOrderResponse(object):
    def __init__(self, success: bool, order_id: str):
        self.__success = success
        self.__order_id = order_id

    def success(self) -> bool:
        return self.__success

    def order_id(self) -> str:
        return self.__order_id

    @staticmethod
    def from_json(data):
        return PlaceOrderResponse(data['success'], data['order_id'])
