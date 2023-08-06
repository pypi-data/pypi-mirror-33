from flask import Flask

from astronaut.rest import space
from astronaut.settings import DevConfig


def create_app(config_object=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.register_blueprint(space.blueprint)
    return app
