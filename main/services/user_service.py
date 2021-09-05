import logging as log
from flask import current_app as app

from main.db import MongoDB
from main.services.blacklist_helper import BlacklistHelper


class UserService:
    """ doc string for UserService """

    def __init__(self):
        super(UserService, self).__init__()
        self.collection = "users"
        self.blacklist = BlacklistHelper()
        self.mongo = MongoDB()

    def user_list(self):
        users = self.mongo.find(self.collection)
        if users:
            for user in users:
                del user["password"]
            return users
        else:
            return []

    def add_user(self, user_obj):
        """ user_obj - user object """
        user = self.mongo.find(self.collection, {"email": user_obj["email"]})
        if not user:
            res = self.mongo.save(self.collection, user_obj)
            return {"status": 0, "response": res}
        else:
            return {"status": -1, "response": f'User with {user_obj["email"]} already existed.'}

    def get_user(self, user_id):
        """ Get User profile by id. ex _id:  """
        res = self.mongo.find_by_id(self.collection, user_id)
        if res:
            del res["password"]
            return "success", res, "ok", 200
        else:
            return "error", [], "Something went wrong.", 400

    def update_user(self, _id, user_obj):
        user = self.mongo.find(self.collection, {"email": user_obj["email"]})
        if not user:
            query = {"$set": user_obj}
            res, res_obj = self.mongo.update(self.collection, _id, query)
            if res:
                del res_obj["password"]
                return "success", res_obj, "ok", 200
            else:
                return "error", "", "Something went wrong.", 400
        else:
            return (
                "error",
                "",
                f'Email {user_obj["email"]} address already in use.',
                400,
            )

    def activate_user(self, email):
        # ToDo : If activated user reattempts, we shouldn't allow
        user = self.mongo.find(self.collection, {"email": email, "active": False})
        if user:
            log.info(user)
            log.info("Found user to activate {}" + user[0]["_id"])
            query = {"$set": {'active': True}}
            res, res_obj = self.mongo.update(self.collection, user[0]["_id"], query)
            if res:
                del res_obj["password"]
                return {"status": 0, "response": f'Activated Successfully'}
            else:
                return {"status": -1, "response": f'Something went wrong.'}
        else:
            return {"status": -1, "response": f'We could not activate'}

    def passwordChange(self, email, new_password):
        # Password change is allowed for activated users only
        user = self.mongo.find(self.collection, {"email": email, "active": True})
        if user:
            log.info("Found user to change password {}" + user[0]["_id"])
            query = {"$set": {'password': new_password}}
            res, res_obj = self.mongo.update(self.collection, user[0]["_id"], query)
            if res:
                del res_obj["password"]
                return {"status": 0, "response": f'Password Changed Successfully'}
            else:
                return {"status": -1, "response": f'Something went wrong.'}
        else:
            return {"status": -1, "response": f'We could not change password'}

    def delete_user(self, user_id):
        return self.mongo.delete(self.collection, user_id)

    def login(self, email):
        """ email as input """
        user = self.mongo.find(self.collection, {"email": email})
        if user:
            user = user[0]
            return user
        else:
            return None

    def save_tokens(self, user_tokens):
        self.blacklist.add_token_to_database(
            user_tokens["access"], app.config["JWT_IDENTITY_CLAIM"]
        )
        self.blacklist.add_token_to_database(
            user_tokens["refresh"], app.config["JWT_IDENTITY_CLAIM"]
        )
