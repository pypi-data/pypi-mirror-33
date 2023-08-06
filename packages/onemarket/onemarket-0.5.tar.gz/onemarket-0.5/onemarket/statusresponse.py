class StatusResponse(object):
    def __init__(self, healthy: bool, error: str):
        self.__healthy = healthy
        self.__error = error

    def healthy(self) -> bool:
        return self.__healthy

    def error(self) -> str:
        return self.__error

    @staticmethod
    def from_json(data):
        return StatusResponse(data['healthy'], data['error'])
