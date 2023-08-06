import logging
import time
from typing import Mapping
from .exchange import Exchange
from .exchangeproxy import ExchangeProxy


class ExchangeFactory(object):
    def __init__(self):
        pass

    @staticmethod
    def instance(config: Mapping[str, str]) -> Exchange:
        logger = logging.getLogger('ExchangeFactory')

        if config['type'] == 'exchange-proxy':
            exchange = ExchangeProxy(config['base_url'])
            while True:
                try:
                    if exchange.status().healthy():
                        return exchange
                except Exception as ex:
                    pass

                logger.warning("Exchange not ready. Sleeping for 10s...")
                time.sleep(10)
