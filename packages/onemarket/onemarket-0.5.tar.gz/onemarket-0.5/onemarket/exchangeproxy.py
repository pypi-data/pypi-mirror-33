from typing import Sequence
from marketmaker import version
from .exchange import Exchange
from .marketdata import MarketData
from .assetpairproperties import AssetPairProperties
from .placeorderrequest import PlaceOrderRequest
from .placeorderresponse import PlaceOrderResponse
from .cancelorderrequest import CancelOrderRequest
from .cancelorderresponse import CancelOrderResponse
from .statusresponse import StatusResponse
import requests


class ExchangeProxy(Exchange):
    def __init__(self, base_url):
        self._base_url = base_url
        self._apiversion = '0'
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'vasilv/' + version.__version__ + ' (+' + version.__url__ + ')'
        })

    def get_time(self) -> int:
        response_json = self._query('/time', 'GET');
        return int(response_json)

    def get_market(self) -> MarketData:
        response_json = self._query('/market', 'GET')
        return MarketData.from_json(response_json)

    def get_assets(self) -> Sequence[AssetPairProperties]:
        response_json = self._query('/assets', 'GET')
        return [AssetPairProperties.from_json(data) for data in response_json]

    def place_order(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        response_json = self._query('/open', 'POST', data=request.to_json())
        return PlaceOrderResponse.from_json(response_json)

    def cancel_order(self, request: CancelOrderRequest) -> CancelOrderResponse:
        response_json = self._query('/cancel', 'POST', data=request.to_json())
        return CancelOrderResponse.from_json(response_json)

    def status(self) -> StatusResponse:
        response_json = self._query('/status', 'GET')
        return StatusResponse.from_json(response_json)

    def _query(self, urlpath, method, data=None, headers=None, timeout=None, auth=None):
        """ Low-level query handling.

        .. note::
           Use :py:meth:`query_private` or :py:meth:`query_public`
           unless you have a good reason not to.

        :param urlpath: API URL path sans host
        :type urlpath: str
        :param urlpath: HTTP method type - one of GET or POST
        :type urlpath: str
        :param data: API request parameters
        :type data: dict
        :param headers: (optional) HTTPS headers
        :type headers: dict
        :param timeout: (optional) if not ``None``, a :py:exc:`requests.HTTPError`
                        will be thrown after ``timeout`` seconds if a response
                        has not been received
        :type timeout: int or float
        :returns: :py:meth:`requests.Response.json`-deserialised Python object
        :raises: :py:exc:`requests.HTTPError`: if response status not successful

        """
        if data is None:
            data = {}
        if headers is None:
            headers = {}

        headers['Content-Type'] = 'application/json'

        url = self._base_url + urlpath

        if method == 'GET':
            response = self._session.get(url, json=data, headers=headers, timeout=timeout, auth=auth)
        elif method == 'POST':
            response = self._session.post(url, json=data, headers=headers, timeout=timeout, auth=auth)
        elif method == 'DELETE':
            response = self._session.delete(url, json=data, headers=headers, timeout=timeout, auth=auth)
        else:
            raise Exception("Method not supported.")

        if response.status_code not in (200, 201, 202):
            response.raise_for_status()

        return response.json()
