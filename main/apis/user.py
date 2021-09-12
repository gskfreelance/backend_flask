from flask_restx import Namespace, Resource, fields
from flask import request
api = Namespace("User", description="User related APIs")
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from main.services.user_helper import UserHelper
from main.services.user_service import UserService
from main.services.fiat_transaction_service import FiatTransactionService
from main.services.wallet_service import WalletService


@api.route("/me")
class UserEnquiry(Resource):
    """docstring for User Enquiry."""

    def __init__(self, arg):
        super(UserEnquiry, self).__init__(arg)
        self.user_service = UserService()
        self.user_helper = UserHelper()

    @jwt_required()
    def get(self):
        """ Get User Details along with Wallet Balances """

        current_user_email = get_jwt_identity()
        user_full_details = self.user_helper.constructFullUserDetails(current_user_email)
        return {"status": "success", 'user': user_full_details}, 201


deposit_inr_model = api.model(
    "DepositInrModel",
    {
        "amount": fields.String(description="Amount to deposit", required=True),
        "txRef": fields.String(description="Payment gateway transaction reference", required=True),
    },
)


@api.route("/deposit_inr")
class DepositINR(Resource):
    """docstring for INR Deposit."""

    def __init__(self, arg):
        super(DepositINR, self).__init__(arg)
        self.user_service = UserService()
        self.user_helper = UserHelper()
        self.fiat_transaction_service = FiatTransactionService()
        self.wallet_service = WalletService()

    @api.expect(deposit_inr_model)
    @jwt_required()
    def post(self):
        """ Deposit INR """
        if "amount" not in request.json or request.json["amount"] == "":
            return api.abort(
                400, "Amount should not be empty.", status="error", status_code=400
            )

        amount = request.json["amount"]

        if "txRef" not in request.json or request.json["txRef"] == "":
            return api.abort(
                400, "txRef should not be empty.", status="error", status_code=400
            )

        txRef = request.json["txRef"]

        current_user_email = get_jwt_identity()
        user_response = self.user_service.get_user_from_email(current_user_email)

        if user_response["status"] == -1:
            return api.abort(
                400, "Could not find user", status="error", status_code=400
            )

        user_id = user_response["response"]["_id"]
        print("depositing for " + user_id)
        transaction_entry = {
            "user_id": user_id,
            "amount": amount,
            "txRef": txRef,
            "type": "Deposit",
            "status": "success" # for MVP, assuming always success
        }
        res = self.fiat_transaction_service.deposit_inr(transaction_entry)
        print(res)

        # Update the Wallet Balance
        res = self.wallet_service.update_balance_for_buy(user_id,"inr", amount)
        print(res)
        return {"status": "success", 'message': ' Amount Deposited'}, 201