
from binance.client import Client
from flask import current_app as app
import requests


class BinanceService:
    """ doc string for BinanceService """

    def __init__(self):
        super(BinanceService, self).__init__()
        self.client = Client(app.config["BINANCE_API_KEY"], app.config["BINANCE_API_SECRET"])
        self.collection = ""

    def getAllTickers(self):
        symbols = []
        try:
            server_time = self.client.get_server_time()
            info = self.client.get_all_tickers()
            wazirx_response = requests.get(app.config["WAZIRX_API_URL"])
            usdt_inr_factor = wazirx_response.json().get("usdtinr").get("last")

            for pair in info:
                if pair["symbol"].endswith("USDT"):
                    # Just a hack - need to get INRUSDT pair to convert this value
                    pair["price_INR"] = float(pair["price"]) * float(usdt_inr_factor)
                    symbols.append(pair)
            return {"assetPrice": symbols, "priceUpdateTime": server_time}, 0
        except Exception as e:
            print(e)
            return {}, -1



