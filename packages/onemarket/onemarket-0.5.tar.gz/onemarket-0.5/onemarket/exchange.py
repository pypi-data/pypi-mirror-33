from typing import Sequence
from .assetpairproperties import AssetPairProperties
from .marketdata import MarketData
from .placeorderrequest import PlaceOrderRequest
from .placeorderresponse import PlaceOrderResponse
from .cancelorderrequest import CancelOrderRequest
from .cancelorderresponse import CancelOrderResponse
from .statusresponse import StatusResponse


class Exchange(object):
    def __init__(self):
        pass

    def get_time(self) -> int:
        raise NotImplementedError("This method should be overwritten.")

    def get_market(self) -> MarketData:
        raise NotImplementedError("This method should be overwritten.")

    def get_assets(self) -> Sequence[AssetPairProperties]:
        raise NotImplementedError("This method should be overwritten.")

    def place_order(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        raise NotImplementedError("This method should be overwritten.")

    def cancel_order(self, request: CancelOrderRequest) -> CancelOrderResponse:
        raise NotImplementedError("This method should be overwritten.")

    def status(self) -> StatusResponse:
        raise NotImplementedError("This method should be overwritten.")
