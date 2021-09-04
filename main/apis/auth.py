import datetime
import logging as log
import re

import jwt
from flask_mail import Mail, Message
from flask_restx import Namespace, Resource, fields

api = Namespace("Authentication", description="Authentication related APIs")
from flask import request
from flask import current_app as app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from main.services.blacklist_helper import BlacklistHelper
from main.services.jwt_service import JWTService
from main.services.user_service import UserService

user_register_model = api.model(
    "SignupModel",
    {
        "name": fields.String(description="Name of the user", required=True),
        "email": fields.String(description="Email address", required=True),
        "password": fields.String(description="password", required=True),
    },
)


@api.route("/auth/register")
class UserRegister(Resource):
    """docstring for UserRegister."""

    def __init__(self, arg):
        super(UserRegister, self).__init__(arg)
        self.jwt_service = JWTService()
        self.blacklist = BlacklistHelper()
        self.user_service = UserService()
        self.mail = Mail(app)

    @api.expect(user_register_model)
    # @jwt_required
    def post(self):
        """ Register new User """
        if "email" not in request.json or request.json["email"] == "":
            return api.abort(
                400, "Email should not be empty.", status="error", status_code=400
            )

        email = request.json["email"]
        if not re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$', email):
            return api.abort(
                400, "Email is not valid.", status="error", status_code=400
            )

        if "password" not in request.json or request.json["password"] == "":
            return api.abort(
                400, "Password should not be empty.", status="error", status_code=400
            )

        if "name" not in request.json or request.json["name"] == "":
            return api.abort(
                400, "Name should not be empty.", status="error", status_code=400
            )
        name = request.json["name"]
        request.json["password"] = self.jwt_service.hash_password(
            request.json["password"]
        )

        # Lets set the status as "pending activation"
        request.json["active"] = "False"
        res = self.user_service.add_user(request.json)

        log.info(res["status"])

        # this means user already exists. Lets send the response and avoid email
        if res["status"] == -1:
            return api.abort(
                400, res["response"], status="error", status_code=400
            )

        res = res["response"]

        if "password" in res:
            del res["password"]

        # We are able to save new user as inactive. Lets send the activation code to email ID provided
        # ToDo : This is costly operation. This should go to offline task management.
        # ToDo : We should ideally just create a task and leave email process to offline job
        exp = datetime.datetime.utcnow() + datetime.timedelta(days=app.config['ACTIVATION_EXPIRE_DAYS'])
        encoded = jwt.encode({'email': email, 'exp': exp},
                             app.config['ENCODE_KEY'], algorithm='HS256')
        message = 'Hello {} \n activation_code = {}'.format(name, encoded)
        msg = Message(recipients=[email],
                      body=message,
                      subject='Activation Code',
                      sender='Flask App')
        self.mail.send(msg)
        log.info(message)
        return {"status": "success", "res": res, "message": "ok"}, 201


user_activation_model = api.model(
    "ActivationModel",
    {
        "activation_code": fields.String(description="Activation Code", required=True),
    },
)


@api.route("/auth/activate")
class UserActivate(Resource):
    """docstring for UserActivate."""

    def __init__(self, arg):
        super(UserActivate, self).__init__(arg)
        self.jwt_service = JWTService()
        self.blacklist = BlacklistHelper()
        self.user_service = UserService()

    @api.expect(user_activation_model)
    # @jwt_required
    def post(self):
        """ Activate new User """
        if "activation_code" not in request.json or request.json["activation_code"] == "":
            return api.abort(
                400, "Activation code should not be empty.", status="error", status_code=400
            )

        activation_code = request.json["activation_code"]
        try:
            decoded = jwt.decode(activation_code, app.config['ENCODE_KEY'], algorithms='HS256')
        except jwt.DecodeError:
            return api.abort(
                400, "Activation code is not valid.", status="error", status_code=400
            )
        except jwt.ExpiredSignatureError:
            return api.abort(
                400, "Activation code has expired.", status="error", status_code=400
            )
        email = decoded['email']
        log.info("Activating {}".format(email))
        res = self.user_service.activate_user(email)
        if "password" in res:
            del res["password"]

        return {"status": "success", "res": res, "message": "ok"}, 201


user_login_model = api.model(
    "LoginModel",
    {
        "email": fields.String(description="Email address", required=True),
        "password": fields.String(description="Password", required=True),
    },
)


@api.route("/auth/login")
class UserLogin(Resource):
    """docstring for UserLogin."""

    def __init__(self, arg):
        super(UserLogin, self).__init__(arg)
        self.jwt_service = JWTService()
        self.user_service = UserService()

    @api.expect(user_login_model)
    def post(self):
        """ User login API """
        if "email" not in request.json or request.json["email"] == "":
            return api.abort(
                400, "Email should not be empty.", status="error", status_code=400
            )

        if "password" not in request.json or request.json["password"] == "":
            return api.abort(
                400, "Password should not be empty.", status="error", status_code=400
            )

        email, password = request.json["email"], request.json["password"]

        request.json["password"] = self.jwt_service.hash_password(password)

        user = self.user_service.login(email)
        if user:
            if user["active"]:
                pass_match = self.jwt_service.check_password(user["password"], password)
            else:
                pass_match = None
        else:
            pass_match = None

        if pass_match:
            del user["password"]
            user["tokens"] = {
                "access": create_access_token(identity=email),
                "refresh": create_refresh_token(identity=email),
            }
            self.user_service.save_tokens(user["tokens"])
            message, status_code = "Login successful.", 200
        else:
            user = []
            message, status_code = "Email or Password combination is wrong OR User is not active.", 401

        return {"status": "success", "res": user, "message": message}, status_code


@api.route("/auth/refreshToken")
class TokenRefresh(Resource):
    """docstring for TokenRefresh."""

    def __init__(self, args):
        super(TokenRefresh, self).__init__()

    @jwt_required(refresh=True)
    def post(self):
        """ Refresh token """
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        self.user_service.save_tokens(access_token)

        return {"status": "success", "access_token": access_token}, 200


@api.route("/auth/logOut")
class UserLogOut(Resource):
    """docstring for Log Out."""

    def __init__(self, args):
        super(UserLogOut, self).__init__()
        self.blacklist = BlacklistHelper()

    @jwt_required()
    def post(self):
        """ User logout API """
        current_user = get_jwt_identity()
        log.info(current_user)
        code, msg = self.blacklist.revoke_token(current_user)
        log.info({code, msg})

        return {"status": "success", "msg": msg}, code


user_change_password_model = api.model(
    "ChangePasswordModel",
    {
        "email": fields.String(description="Email address", required=True),
        "password": fields.String(description="Old Password", required=True),
        "new_password": fields.String(description="New Password", required=True),
    },
)


@api.route("/auth/changePassword")
class ChangePassword(Resource):
    """docstring for Password Update."""

    def __init__(self, args):
        super(ChangePassword, self).__init__()

    @jwt_required()
    def post(self):
        """ Password Change - WIP """
        if "email" not in request.json or request.json["email"] == "":
            return api.abort(
                400, "Email should not be empty.", status="error", status_code=400
            )

        email = request.json["email"]
        if not re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$', email):
            return api.abort(
                400, "Email is not valid.", status="error", status_code=400
            )

        if "password" not in request.json or request.json["password"] == "":
            return api.abort(
                400, "Password should not be empty.", status="error", status_code=400
            )
        password = request.json["password"]

        if "new_password" not in request.json or request.json["new_password"] == "":
            return api.abort(
                400, "New password should not be empty.", status="error", status_code=400
            )

        new_password = request.json["new_password"]

        # check if new_password != password
        if new_password == password:
            return api.abort(
                400, "New password should not be same as old password.", status="error", status_code=400
            )

        # all good to change password

        return {"status": "success", "msg": 'This is WIP. Not implemented yet'}, 200
