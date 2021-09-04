import pathlib

import coloredlogs
from flask_restx import Api

# local imports
from main import create_app
from main.apis.auth import api as auth

coloredlogs.install()

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


# Run Server
if __name__ == '__main__':
    app.run()
