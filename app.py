import pathlib

from flask_restx import Api

# local imports
from main import create_app, create_socket
from main.apis.auth import api as auth
from main.apis.user import api as user
from main.apis.binance import api as binance

authorizations = {
    'token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}
app = create_app()

api = Api(app, authorizations=authorizations, version='1.0', title='API docs',
          description='Flask App with REST APIs for Auth',
          doc='/docs'
          )

app.config['ROOT_DIR'] = pathlib.Path(__file__).parent.absolute()

# Endpoints
api.add_namespace(auth, path='/v1')
api.add_namespace(user, path='/v1')
api.add_namespace(binance, path='/v1')
# socket_io = create_socket(app)

# Run Server
if __name__ == '__main__':
    # socket_io.run(app)
    app.run()
