# Bunch of configurations for system
# ToDO : move these to Config class to have environement specific configurations
# ToDo : Read sensitive data like secrets, passwords etc from OS Environment variable

DEBUG = True

# sensitive, move this to os env
ENCODE_KEY = 'mysuperscretkey'

# Email Server Config
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'kachrakachra0@gmail.com'
MAIL_PASSWORD = 'xxprvkiurepmbczo'
MAIL_DEFAULT_SENDER = 'from@example.com'
ACTIVATION_EXPIRE_DAYS = 2


# Mongo DB Config
DB_HOST = 'cluster0.jj6wh.mongodb.net'
DB_PORT = 27017
DB_NAME = 'myFirstDatabase'
DB_USER = 'testuser'
# move this to os.env
DB_PASSWORD = 'test123'

