from datetime import datetime
from main.database.db import MongoDB


class FiatTransactionService:
    """ doc string for Fiat Transaction Service """

    def __init__(self):
        super(FiatTransactionService, self).__init__()
        self.collection = "fiat_transactions"
        self.mongo = MongoDB()

    def deposit_inr(self, transaction_entry):
        transaction_entry["txDate"] = datetime.now()
        res = self.mongo.save(self.collection, transaction_entry)
        return res

