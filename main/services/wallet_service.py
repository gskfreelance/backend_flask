from main.database.db import MongoDB


class WalletService:
    """ doc string for WalletService """

    def __init__(self):
        super(WalletService, self).__init__()
        self.collection = "wallet_balance"
        self.mongo = MongoDB()

    def get_wallet_balance(self, user_id):
        balances = self.mongo.find(self.collection, {"user_id" : user_id})
        if balances:
            for balance in balances:
                print(balance)
            return balances
        else:
            return []

    def update_balance_for_buy(self, user_id, symbol, quantity):
        """ doc string for Update balance """
        balance_entry = self.mongo.find(self.collection, {"user_id": user_id, "symbol": symbol})
        if not balance_entry:
            print("User has no balance for " + symbol)
            balance_entry = {
                "user_id": user_id,
                "symbol": symbol,
                "quantity": quantity
            }
            res = self.mongo.save(self.collection, balance_entry)
            return {"status": 0, "response": res}
        else:
            print("User existing balance for " + symbol + " is " + str(balance_entry[0]["quantity"]))
            new_quantity = float(balance_entry[0]["quantity"]) + quantity
            query = {"$set": {'quantity': new_quantity}}
            res, res_obj = self.mongo.update(self.collection, balance_entry[0]["_id"], query)
            return {"status": 0, "response": res_obj}

    def update_balance_for_sell(self, user_id, symbol, quantity):
        """ doc string for Update balance """
        balance_entry = self.mongo.find(self.collection, {"user_id": user_id, "symbol": symbol})
        if not balance_entry:
            print("User has no balance for " + symbol)
            return {"status": -1, "response": "Shouldn't sell"}
        else:
            new_quantity = float(balance_entry[0]["quantity"]) - quantity
            query = {"$set": {'quantity': new_quantity}}
            res, res_obj = self.mongo.update(self.collection, balance_entry[0]["_id"], query)
            return {"status": 0, "response": res_obj}