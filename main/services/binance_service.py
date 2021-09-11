from flask import current_app as app
from binance.client import Client
from decimal import Decimal
import datetime
from objdict import ObjDict


class BinanceService:
    """ doc string for BinanceService """

    def __init__(self):
        super(BinanceService, self).__init__()
        self.client = Client(app.config["BINANCE_API_KEY"], app.config["BINANCE_API_SECRET"])

    def getAllTickers(self):
        symbols = []
        server_time = self.client.get_server_time()
        info = self.client.get_all_tickers()
        for pair in info:
            if pair["symbol"].endswith("USDT"):
                # Just a hack - need to get INRUSDT pair to convert this value
                pair["price_INR"] = Decimal(pair["price"]) * 2
                symbols.append(pair)
        return {"assetPrice": symbols, "priceUpdateTime": server_time}, 0


