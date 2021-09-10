import logging as log
from flask import current_app as app
from main.db import MongoDB
from binance.client import Client


class BinanceService:
    """ doc string for BinanceService """
    def __init__(self):

        super(BinanceService, self).__init__()
        self.mongo = MongoDB()
        self.client = Client(app.config["binance_api_key"], app.config["binance_api_secret"])
        self.client.API_URL = app.config["binance_api_url"]

    def getSymbolTicker(self, symbol="BTCUSDT"):
        price = self.client.get_symbol_ticker(symbol)
        return price
