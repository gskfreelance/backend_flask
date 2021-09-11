import datetime
import logging as log

from flask_restx import Namespace, Resource, fields

api = Namespace("Binance", description="Binance related APIs")
from flask import request
from flask import current_app as app


from main.services.jwt_service import JWTService

from main.services.binance_service import BinanceService


@api.route("/binance/getLatestPrice")
class BinanceTicker(Resource):
    """docstring for Binance Price."""

    def __init__(self, arg):
        super(BinanceTicker, self).__init__(arg)
        self.jwt_service = JWTService()
        self.binance_service = BinanceService()

    # @jwt_required
    def post(self):
        """ Get Latest Price from Binance """

        response, status_code = self.binance_service.getAllTickers()
        if status_code == 0:
            return {"status": "success", "data": response}, 201
        else:
            return {"status": "error", "data": ""}, 400
