import time

from app import db
from app.api import constants
from app.api.errors import error_response
from app.models import Analyst, Job, Worker, Command, to_collection_dict
from app.queue.rabbit_queue import RQueue
from datetime import datetime
from flask import Blueprint
from flask import jsonify, request, Response
from flask_jwt_extended import jwt_required
from sqlalchemy import update

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

    response = jsonify(worker.to_dict())
    response.status_code = 200

    return response


# Job routes


@bp.route('/jobs', methods=['POST'])
# @jwt_required
def create_job():

    start = time.time()

    data = request.get_json(force=True) or {}

    # Validate data
    if not _is_valid(data, constants.JOB_REQ):
        return error_response(400, 'Missing values.')

    analyst = Analyst.query.get(data['analyst_id'])

    if data['targets'] == 'all':
        query = db.session.query(Worker.target_queue).all()
        targets = [hostname[0] for hostname in query]
        data['targets'] = targets
    else:
        targets = data['targets']

    # Save job into db
    job = Job()
    job.from_dict(data)
    analyst.jobs.append(job)

    db.session.add(analyst)

    # Flushing data base to retrieve job id.
    db.session.flush()

    command_list = data['description']

    job_request = job.to_dict()

    queue = RQueue()

    if len(command_list) > 0:
        for target_queue in targets:
            worker = Worker.query.filter_by(target_queue=target_queue).first()
            for i, cmd in enumerate(command_list):
                command = Command()
                command.from_dict(cmd, job_id=job.job_id, worker_id=worker.worker_id)
                db.session.add(command)
                db.session.flush()

                job_request['description'][i]['command_id'] = command.command_id

            job_request['targets'] = target_queue

            # Send job request to queue
            db.session.commit()
            if not queue.send_job(job_request):
                return error_response(500, 'Error while sending message to message broker')

    else:
        return error_response(400, 'A job must contain at least one command.')

    queue.close()

    # Once the queue receives the command, return response.
    response = jsonify(job_request)
    response.status_code = 202

    print(time.time() - start)

    return response


@bp.route('/jobs', methods=['GET'])
@jwt_required
def get_jobs():
    response = Job.query.all()

    response = jsonify(to_collection_dict(response))
    response.status_code = 200

    return response


@bp.route('/jobs/<int:job_id>', methods=['GET'])
@jwt_required
def get_job(job_id: int):

    job = Job.query.get(job_id)

    if job is None:
        return error_response(404, 'Resource not found.')

    response = jsonify(job.to_dict())
    response.status_code = 200

    return response


@bp.route('/jobs/results', methods=['PUT'])
# @jwt_required
def upload_results():

    data = request.get_json(force=True) or {}

    stmt = update(Command).where(Command.command_id == data['command_id']).\
        values(response=data['response'], status='completed')

    insert = db.session.execute(stmt)

    if insert:
        command = db.session.query(Command).filter(Command.command_id == data['command_id']).first()

        # Check job and see if all jobs are completed to update the job status
        query = db.session.query(Command).join(Job).filter(command.job_id == Job.job_id).all()

        _check_job_completion(command=command, query_result=query)

        db.session.commit()
    else:
        return error_response(500, 'Error while processing the upload.')

    return Response(status=204, mimetype='application/json')


@bp.route('/jobs/results/<int:job_id>', methods=['GET'])
@jwt_required
def get_results(job_id: int):
    job = Job.query.get(job_id)
    payload = job.to_dict()

    commands = db.session.query(Command).filter(Command.job_id == job_id).all()

    if not len(commands):
        return error_response(400, 'Invalid ID provided.')

    payload['commands'] = to_collection_dict(commands)

    response = jsonify(payload)
    response.status_code = 200

    return response


@bp.route('/heartbeats', methods=['PUT'])
def heartbeat_response():

    data = request.get_json(force=True) or {}

    if 'target_queue' not in data:
        return error_response(400, 'Missing field target_queue.')

    worker = Worker.query.filter_by(target_queue=data['target_queue']).first()

    if worker is None:
        return error_response(404, 'Resource not available.')

    if worker.status == 'offline':
        stmt = update(Worker)\
            .where(Worker.target_queue == worker.target_queue)\
            .values(status='active', last_seen=datetime.now())
    else:
        stmt = update(Worker)\
            .where(Worker.target_queue == worker.target_queue)\
            .values(last_seen=datetime.now())

    query = db.session.execute(stmt)

    if not query:
        return error_response(500, 'Error while processing heartbeat update.')

    db.session.commit()

    return Response(status=204, mimetype='application/json')


def _check_job_completion(command, query_result):
    """Checks if all commands that are part of a job have been completed, if so, update the job's status."""
    count = 0
    for command in query_result:
        if command.status == 'completed':
            count += 1

    if count == len(query_result):
        db.session.query(Job)\
            .filter(command.job_id == Job.job_id)\
            .update(
            {
                'status': 'completed',
                'end_time': datetime.now()
            }
        )
