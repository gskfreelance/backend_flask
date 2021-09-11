import os
# Bunch of configurations for system
# ToDO : move these to Config class to have environement specific configurations


DEBUG = True


ENCODE_KEY = os.getenv("ENCODE_KEY")

# Email Server Config
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = 'from@example.com'
ACTIVATION_EXPIRE_DAYS = 2


# Mongo DB Config
DB_HOST = os.getenv("DB_HOST")
DB_PORT = 27017
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Binance Keys
BINANCE_API_KEY = os.getenv("binance_api")
BINANCE_API_SECRET = os.getenv("binance_secret")
BINANCE_API_URL = "https://testnet.binance.vision/api"
