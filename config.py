import os
# Bunch of configurations for system
# ToDO : move these to Config class to have environement specific configurations
# ToDo : Read sensitive data like secrets, passwords etc from OS Environment variable

DEBUG = True

# sensitive, move this to os env
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
# move this to os.env
DB_PASSWORD = os.getenv("DB_PASSWORD")

