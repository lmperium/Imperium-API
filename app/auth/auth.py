from flask import Blueprint
from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token
from imperium_api.api import errors
from imperium_api.models import Analyst

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():

    data = request.get_json(force=True) or {}

    try:
        email = data['email']
        password = data['password']
    except KeyError:
        return errors.error_response(status_code=400, message='Must include email and password to log in.')

    # Check that the user exists
    analyst = Analyst.query.filter_by(email=email).first()

    # Validate password if analyst exists
    if analyst and analyst.check_password(password):
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

        response = jsonify(dict(access_token=access_token, refresh_token=refresh_token))
        response.status_code = 200

        return response
    else:
        return errors.error_response(status_code=401, message='Incorrect Email or password')
