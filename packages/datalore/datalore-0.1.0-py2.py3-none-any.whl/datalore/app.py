from flask import Flask

from datalore.rest import bay
from datalore.settings import DevConfig


def create_app(config_object=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.register_blueprint(bay.blueprint)
    return app
