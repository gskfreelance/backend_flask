from flask_restx import Namespace, Resource, fields
from flask import request
api = Namespace("Binance", description="Binance related APIs")

from main.services.jwt_service import JWTService
from main.services.user_service import UserService
from main.services.user_helper import UserHelper
from main.services.wallet_service import WalletService
from main.services.order_service import OrderService


from main.services.binance_service import BinanceService
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)


@api.route("/binance/getLatestPrice")
class BinanceTicker(Resource):
    """docstring for Binance Price."""

    def __init__(self, arg):
        super(BinanceTicker, self).__init__(arg)
        self.binance_service = BinanceService()

    # @jwt_required
    def get(self):
        """ Get Latest Price from Binance """

        response, status_code = self.binance_service.getAllTickers()
        if status_code == 0:
            return {"status": "success", "data": response}, 201
        else:
            return {"status": "error", "data": ""}, 400


binance_place_order = api.model(
    "OrderModel",
    {
        "symbol": fields.String(description="Symbol", required=True),
        "side": fields.String(description="Buy or Sell", required=True),
        "price": fields.String(description="Unit Price", required=True),
        "orderType": fields.String(description="Market or Limit", required=True),
        "pairQuantity": fields.String(description="pairQuantity", required=True),
    },
)


@api.route("/binance/placeOrder")
class BinancePlaceOrder(Resource):
    """docstring for Binance Place Order"""

    def __init__(self, arg):
        super(BinancePlaceOrder, self).__init__(arg)
        self.jwt_service = JWTService()
        self.user_service = UserService()
        self.wallet_service = WalletService()
        self.binance_service = BinanceService()
        self.order_service = OrderService()
        self.user_helper = UserHelper()

    @api.expect(binance_place_order)
    @jwt_required()
    def post(self):
        """ Binance Place Order API -  - WIP DO NOT USE"""

        email = get_jwt_identity()

        user = self.user_helper.constructFullUserDetails(email)

        if "symbol" not in request.json or request.json["symbol"] == "":
            return api.abort(
                400, "Symbol should not be empty.", status="error", status_code=400
            )

        symbol = request.json["symbol"]

        if "side" not in request.json or request.json["side"] == "":
            return api.abort(
                400, "Side should be not be empty.", status="error", status_code=400
            )

        side = request.json["side"]

        if "side" not in ["BUY", "SELL"]:
            return api.abort(
                400, "Side should be BUY Or SELL.", status="error", status_code=400
            )

        if "orderType" not in request.json or request.json["orderType"] == "":
            return api.abort(
                400, "Order Type should be not be empty.", status="error", status_code=400
            )

        order_type = request.json["orderType"]

        if "order_type" not in ["MARKET"]:
            return api.abort(
                400, "Only MARKET type order is supported.", status="error", status_code=400
            )

        if "pairQuantity" not in request.json or request.json["pairQuantity"] == "":
            return api.abort(
                400, "Quantity should not be empty.", status="error", status_code=400
            )
        pair_quantity = request.json["pairQuantity"]

        if "price" not in request.json or request.json["price"] == "":
            return api.abort(
                400, "Price should not be empty.", status="error", status_code=400
            )
        price = request.json["price"]

        order_object = {
            "user": user,
            "symbol": symbol,
            "price": price,
            "pairQuantity": pair_quantity
        }

        response = self.order_service.place_order(order_object)
        if response.status == -1:
            return {"status": "failure", "message": response.message}, 400
        else:
            return {"status": "success", "message": response.message}, 200




