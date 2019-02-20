from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from instance.config import app_config

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'SECRET'

    # Blueprint register
    from app.api.analysts import bp as api_bp
    from app.auth.auth import bp as auth_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')

    db.init_app(app)
    jwt.init_app(app)

    return app
