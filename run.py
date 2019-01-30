from app import create_app, db
from flask_migrate import Migrate
from app.api import bp as api_bp
from app.auth import bp as auth_bp
from app.errors import bp as errors_bp

app = create_app('development')

app.register_blueprint(api_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(errors_bp)

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()
