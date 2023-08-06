class CancelOrderResponse(object):
    def __init__(self, success: bool, error: str):
        self.__success = success
        self.__error = error

    def success(self) -> bool:
        return self.__success

    def error(self) -> str:
        return self.__error

    @staticmethod
    def from_json(data):
        return CancelOrderResponse(data['success'], data['error'])