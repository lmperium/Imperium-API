from app.api.errors import error_response
from app.models import Analyst
from flask import Blueprint
from flask import jsonify, request

bp = Blueprint('api', __name__)


@bp.route('/analysts/<int:analyst_id>', methods=['GET'])
def get_analyst(analyst_id: int):
    analyst = Analyst.query.get(analyst_id)

    if analyst is None:
        return error_response(404, 'Resource not found.')

    return jsonify(analyst.to_dict())


@bp.route('/analysts', methods=['GET'])
def get_analysts():
    response = Analyst.query.all()

    if response is None:
        return error_response(404, 'Resource not found.')

    return jsonify(Analyst.to_collection_dict(response))


@bp.route('/analysts', methods=['POST'])
def register_analyst():
    data = request.get_json()
    print(data)
    pass
