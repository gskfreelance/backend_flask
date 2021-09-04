from flask import current_app as app, jsonify


class JWTService:
    """ doc str """

    def __init__(self):
        super(JWTService, self).__init__()
        self.__jwt_init()

    def hash_password(self, pass_string):
        return app.config["flask_bcrypt"].generate_password_hash(pass_string)

    def check_password(self, pass_hash, pass_string):
        return app.config["flask_bcrypt"].check_password_hash(pass_hash, pass_string)

    def __jwt_init(self):
        jwt = app.config["jwt"]

        @jwt.expired_token_loader
        def expired_token_callback():
            return (
                jsonify({"msg": "The token has expired", "error": "token_expired"}),
                401,
            )

        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            return (
                jsonify(
                    {"msg": "Signature verification failed", "error": "invalid_token"}
                ),
                401,
            )

        @jwt.unauthorized_loader
        def missing_token_callback(error):
            return (
                jsonify(
                    {
                        "msg": "Request does not contain an access token",
                        "error": "authorization_required",
                    }
                ),
                401,
            )

        @jwt.needs_fresh_token_loader
        def token_not_fresh_callback():
            return (
                jsonify(
                    {"msg": "The token is not fresh", "error": "fresh_token_required"}
                ),
                401,
            )

        @jwt.revoked_token_loader
        def revoked_token_callback():
            return (
                jsonify(
                    {"msg": "The token has been revoked", "error": "token_revoked"}
                ),
                401,
            )
