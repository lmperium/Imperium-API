from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from instance.config import app_config

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Blueprint register
    from app.api import bp as api_bp
    from app.auth import bp as auth_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp)

    db.init_app(app)

    return app
