from flask import Flask

from models import db


def create_app():
    app = Flask(__name__)

    app.config.from_pyfile('config.py')

    app.config.from_envvar('MONITOR_CONFIG', silent=True)

    db.init_app(app)

    return app
