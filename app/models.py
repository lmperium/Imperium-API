from app import db
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSON
from werkzeug.security import generate_password_hash, check_password_hash


def to_collection_dict(response) -> dict:
    """
    Convert a collection of items into a Python dictionary object.
    :param response: SQLAlchemy query.all() Tuple
    :return: dictionary object data containing the list of items
    """

    data = {
        'objects': [item.to_dict() for item in response]
    }

    return data


class Analyst(db.Model):

    __tablename__ = 'analyst'

    analyst_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(60), unique=True, index=True, nullable=False)
    username = db.Column(db.String(100), unique=True, index=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    registered_date = db.Column(db.DateTime, server_default=text('now()'), nullable=False)
    jobs = db.relationship('Job', backref='Analyst', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=15)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self, include_email=False):
        data = {
            'analyst_id': self.analyst_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'registered_date': self.registered_date
        }

        if include_email:
            data['email'] = self.email

        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'first_name', 'last_name']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])


class Command(db.Model):

    __tablename__ = 'command'

    command_id = db.Column(db.Integer, primary_key=True)
    command_name = db.Column(db.String(50), index=True, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    response = db.Column(db.Text, nullable=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.job_id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.worker_id'))

    def from_dict(self, data, job_id, worker_id):
        setattr(self, 'status', 'pending')
        setattr(self, 'job_id', job_id)
        setattr(self, 'worker_id', worker_id)
        setattr(self, 'command_name', data['module'])

    def to_dict(self):
        data = dict(
            command_id=self.command_id,
            command_name=self.command_name,
            status=self.status,
            response=self.response
        )

        return data


class Job(db.Model):
    __tablename__ = 'job'

    job_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), nullable=False)
    target = db.Column(db.String(250), nullable=False)
    description = db.Column(JSON, nullable=False)
    start_time = db.Column(db.DateTime, server_default=text('now()'), nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    analyst_id = db.Column(db.Integer, db.ForeignKey('analyst.analyst_id'))

    def from_dict(self, data):
        for field in ['analyst_id', 'job_id', 'name', 'targets', 'description']:
            if field in data:
                if field == 'targets':
                    setattr(self, "target", data[field])
                else:
                    setattr(self, field, data[field])
        setattr(self, 'status', 'Pending')

    def to_dict(self):
        data = dict(
            job_id=self.job_id,
            name=self.name,
            targets=self.target,
            description=self.description,
            start_time=self.start_time,
            end_time=self.end_time,
            status=self.status,
            tracking=dict(url=f'http://localhost:5000/api/jobs/results/{self.job_id}')
        )
        return data


class Worker(db.Model):

    __tablename__ = 'worker'

    worker_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hostname = db.Column(db.String(255), unique=True, index=True, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    target_queue = db.Column(db.String(255), nullable=False, index=True)
    registered_date = db.Column(db.DateTime, server_default=text('now()'), nullable=False)
    last_seen = db.Column(db.DateTime, server_default=text('now()'), nullable=False)
    startup_info = db.Column(JSON)

    def from_dict(self, data):
        """ Convert json data to a Worker object and initialize fields."""
        setattr(self, 'target_queue', self._generate_queue_name(data))
        setattr(self, 'hostname', data['hostname'])
        setattr(self, 'status', 'active')
        setattr(self, 'startup_info', data['startup_info'])

    def to_dict(self):
        data = {
            'worker_id': self.worker_id,
            'hostname': self.hostname,
            'registered_date': self.registered_date,
            'status': self.status,
            'target_queue': self.target_queue,
            'last_seen': self.last_seen,
            'startup_info': self.startup_info
        }

        return data

    @staticmethod
    def _generate_queue_name(data):
        queue_name = 'imp.wk.'
        return queue_name + data['hostname']
