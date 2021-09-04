import datetime
import logging as log

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
)

import config
from .db import MongoDB


def create_app():
    app = Flask(__name__)

    app.config.from_object(config)
    app.config["log"] = log

    cors = CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"

    # Configs needed for JWT service
    # Move this to env variable
    app.config["JWT_SECRET_KEY"] = "9MZbGqQHaC47SSKyKaTK"
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=10)
    app.config["jwt"] = JWTManager(app)
    app.config["flask_bcrypt"] = Bcrypt(app)
    jwt = app.config["jwt"]

    # Swagger UI configs
    app.config.SWAGGER_UI_JSONEDITOR = True
    app.config.SWAGGER_UI_DOC_EXPANSION = "none"  # none, list, full

    with app.app_context():
        db = MongoDB()

    # @jwt.token_in_blocklist_loader
    # def check_if_token_in_blacklist(decrypted_token):
    #     blacklist = set()
    #     jti = decrypted_token["jti"]
    #     return jti in blacklist

    @app.route("/")
    def hello_world():
        # render home template
        return "Hello, World!"

    return app
