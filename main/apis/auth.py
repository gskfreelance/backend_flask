import datetime
import logging as log
import random
import re

import jwt
# from flask_mail import Mail, Message
from sendgrid import SendGridAPIClient
from flask_restx import Namespace, Resource, fields
from sendgrid.helpers.mail import Mail

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
        # request.json["active"] = False
        # For MVP, we are bypassing activation process
        request.json["active"] = True
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
        # ToDo : This is costly operation. For MVP, this is ok but for PROD this should go to offline task management.
        # ToDo : Do we need this as OTP or activation string
        exp = datetime.datetime.utcnow() + datetime.timedelta(days=app.config['ACTIVATION_EXPIRE_DAYS'])
        encoded = jwt.encode({'email': email, 'exp': exp},
                             app.config['ENCODE_KEY'], algorithm='HS256')
        message = 'Hello {}, <br /> Your activation code is <strong>{}</strong>'.format(name, encoded)

        message = Mail(from_email='contactcarretorg@gmail.com', to_emails=email, subject='OTP for login validation', html_content=message)
        try:
            sg = SendGridAPIClient('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')
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
            return {"status": "success", 'message': ' Email sent'}, 201
        except Exception as e:
            print(e.message)
            return {"status": "error",  'message': e.message}, 400


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

        if res["status"] == -1:
            return api.abort(
                400, res["response"], status="error", status_code=400
            )
        if "password" in res:
            del res["password"]

        return {"status": "success", "message": "ok"}, 201


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
        super(TokenRefresh, self).__init__(args)
        self.user_service = UserService()

    @jwt_required(refresh=True)
    def post(self):
        """ Refresh token """
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        self.user_service.save_tokens(access_token)

        return {"status": "success", "access_token": access_token}, 200


user_change_password_model = api.model(
    "ChangePasswordModel",
    {
        "password": fields.String(description="Old Password", required=True),
        "new_password": fields.String(description="New Password", required=True),
    },
)


@api.route("/auth/changePassword")
class ChangePassword(Resource):
    """docstring for Password Update."""

    def __init__(self, args):
        super(ChangePassword, self).__init__(args)
        self.jwt_service = JWTService()
        self.user_service = UserService()

    @api.expect(user_change_password_model)
    @jwt_required()
    def post(self):
        """ Password Change """
        current_user_email = get_jwt_identity()
        print(current_user_email)

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
        new_password = self.jwt_service.hash_password(new_password)
        resp = self.user_service.passwordChange(current_user_email, new_password)

        if resp["status"] == -1:
            return api.abort(
                400, resp["response"], status="error", status_code=400
            )

        return {"status": "success", "msg": 'Password Changed Successfully'}, 200


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
