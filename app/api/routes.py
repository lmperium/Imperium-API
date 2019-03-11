from app import db
from app.api import constants
from app.api.errors import error_response
from app.models import Analyst, Job, Worker, Command, to_collection_dict
from app.queue.rabbit_queue import RQueue
from flask import Blueprint
from flask import jsonify, request
from flask_jwt_extended import jwt_required

bp = Blueprint('api', __name__)

# Analyst routes


@bp.route('/analysts/<int:analyst_id>', methods=['GET'])
@jwt_required
def get_analyst(analyst_id: int):
    analyst = Analyst.query.get(analyst_id)

    if analyst is None:
        return error_response(404, 'Resource not found.')

    return jsonify(analyst.to_dict())


@bp.route('/analysts', methods=['GET'])
@jwt_required
def get_analysts():
    response = Analyst.query.all()

    return jsonify(to_collection_dict(response))


@bp.route('/analysts', methods=['POST'])
def register_analyst():
    data = request.get_json(force=True) or {}

    # Validate required fields
    if not _is_valid(data, constants.ANALYST_REQ):
        return error_response(status_code=400, message='Missing values.')

    if _user_exists(data):
        return error_response(status_code=409, message='Analyst already registered')

    analyst = Analyst()

    # Convert received data to Analyst object
    analyst.from_dict(data=data, new_user=True)

    db.session.add(analyst)
    db.session.commit()

    response = jsonify(analyst.to_dict(include_email=True))
    response.status_code = 201
    return response


def _is_valid(data, requirements):
    for field in requirements:
        if field not in data:
            return False

    return True


def _user_exists(data):
    if Analyst.query.filter_by(username=data['username']).first():
        return True

    if Analyst.query.filter_by(email=data['email']).first():
        return True

    return False


# Worker routes


@bp.route('/workers', methods=['GET'])
@jwt_required
def get_workers():

    response = Worker.query.all()

    return jsonify(to_collection_dict(response))


@bp.route('/workers', methods=['POST'])
def register_worker():
    data = request.get_json(force=True)

    if Worker.query.filter_by(hostname=data['hostname']).first():
        return error_response(409, 'Worker already registered.')

    worker = Worker()
    worker.from_dict(data)

    db.session.add(worker)
    db.session.commit()

    response = jsonify(worker.to_dict())
    response.status_code = 201

    return response


@bp.route('/workers/<int:worker_id>', methods=['GET'])
@jwt_required
def get_worker(worker_id: int):

    worker = Worker.query.get(worker_id)

    if worker is None:
        return error_response(404, 'Resource not found.')

    return jsonify(worker.to_dict())


# Job routes


@bp.route('/jobs', methods=['POST'])
@jwt_required
def create_job():
    data = request.get_json(force=True) or {}

    # TODO validate if it is a valid command.

    # Validate data
    if not _is_valid(data, constants.JOB_REQ):
        return error_response(400, 'Missing values.')

    analyst = Analyst.query.get(data['analyst_id'])
    worker = Worker.query.filter_by(target_queue=data['target']).first()

    # Save job into db
    job = Job()
    job.from_dict(data)

    analyst.jobs.append(job)

    db.session.add(analyst)
    # Flushing data base to retrieve job id.
    db.session.flush()

    # Save command to database
    command = Command()
    command.from_dict(data['description'], job.job_id, worker.worker_id)

    db.session.add(command)

    db.session.commit()
    # Send job description to queue
    queue = RQueue()

    if not queue.send_job(job.to_dict()):
        return error_response(500, 'Error while sending message to message broker')

    # Once the queue receives the command, return response.
    # TODO - Return href and id of job/command in the response.
    response = jsonify(job.to_dict())
    response.status_code = 202

    return response


@bp.route('/jobs', methods=['GET'])
@jwt_required
def get_jobs():
    response = Job.query.all()

    return jsonify(to_collection_dict(response))


@bp.route('/jobs/<int:job_id>', methods=['GET'])
@jwt_required
def get_job(job_id: int):

    job = Job.query.get(job_id)

    if job is None:
        return error_response(404, 'Resource not found.')

    return jsonify(job.to_dict())


@bp.route('/jobs/results', methods=['PUT'])
@jwt_required
def upload_results():
    pass


@bp.route('/jobs/results/<int:job_id>', methods=['GET'])
@jwt_required
def get_results():
    pass
