import logging as log

from flask import current_app as app

from main.database.db import MongoDB
from main.services.wallet_service import WalletService


class OrderService:
    """ doc string for OrderService """

    def __init__(self):
        super(OrderService, self).__init__()
        self.collection = "orders"
        self.mongo = MongoDB()
        self.wallet_service = WalletService()

    def orders_list(self, user_id):
        """ List orders for the user """
        orders = self.mongo.find(self.collection, {"user_id" : user_id})
        if orders:
            return orders
        else:
            return []

    def place_order(self, order_entry):
        """ Assume INR based orders. """
        user = order_entry["user"]
        symbol = order_entry["symbol"]
        price = order_entry["price"]
        pair_quantity = order_entry["pairQuantity"]

        # Check if user has sufficient INR to purchase
        if order_entry["side"] == "BUY":
            wallet_balances = user["Balances"]
            for balance_entry in wallet_balances:
                if balance_entry["symbol"] == "inr":
                    inr_balance = balance_entry["quantity"]

            if inr_balance <= order_entry["pairQuantity"]:
                return {"status": -1, "message": "Insufficient Balance"}

            # all is good - perform buy
            # buy symbol + sell INR

            order_entry = {
                "user_id": user["_id"],
                "symbol": symbol,
                "price": price,
                "pairQuantity": pair_quantity,
                "status": "ToBeExecuted"
            }

            self.mongo.save(self.collection, order_entry)
            self.wallet_service.update_balance_for_sell(user["UserInfo"]["_id"], "inr", price * pair_quantity)
            self.wallet_service.update_balance_for_buy(user["UserInfo"]["_id"], symbol, pair_quantity)
            return {"status": 0, "message": "Order successfully placed"}
        else:
            # Sell operation
            wallet_balances = user["Balances"]
            for balance_entry in wallet_balances:
                if balance_entry["symbol"] == symbol:
                    balance = balance_entry["quantity"]

            if balance <= order_entry["pairQuantity"]:
                return {"status": -1, "message": "Insufficient Balance"}

            # all is good - perform buy
            # buy symbol + sell INR

            order_entry = {
                "user_id": user["_id"],
                "symbol": symbol,
                "price": price,
                "pairQuantity": pair_quantity,
                "status": "ToBeExecuted"
            }

            self.mongo.save(self.collection, order_entry)
            self.wallet_service.update_balance_for_sell(user["UserInfo"]["_id"], symbol,pair_quantity)
            self.wallet_service.update_balance_for_buy(user["UserInfo"]["_id"], "inr",  price * pair_quantity)
            return {"status": 0, "message": "Order successfully placed"}