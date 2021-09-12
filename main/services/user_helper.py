from datetime import datetime

from flask_jwt_extended import decode_token
from main.services.user_service import UserService
from main.services.wallet_service import WalletService


class UserHelper:
    """ Helper file to handle the User Details. """

    def __init__(self):
        super(UserHelper, self).__init__()
        self.user_service = UserService()
        self.wallet_service = WalletService()

    def constructFullUserDetails(self, email):
        """
        From the user email, this method constructs all user details
        """
        user_details = None
        user_response = self.user_service.get_user_from_email(email)
        if user_response["status"] == 0:
            user_details = user_response["response"]

        balance_entries = self.wallet_service.get_wallet_balance(user_details["_id"])

        return {"UserInfo": user_details, "Balances": balance_entries}, 200