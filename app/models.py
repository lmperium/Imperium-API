from app import db
from sqlalchemy.dialects.postgresql import JSON
from werkzeug.security import generate_password_hash, check_password_hash


class Analyst(db.Model):

    __tablename__ = 'analyst'

    analyst_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(60), unique=True, index=True, nullable=False)
    username = db.Column(db.String(100), unique=True, index=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    registered_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

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

    @staticmethod
    def to_collection_dict(response) -> dict:
        """
        Convert a collection of items into a Python dictionary object.
        :param response: SQLAlchemy query.all() Tuple
        :return: dictionary object data containing the list of items
        """

        data = {
            'analysts': [item.to_dict() for item in response]
        }

        return data


class Job(db.Model):
    __tablename__ = 'job'

    job_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    target = db.Column(db.String(250), nullable=False)
    description = db.Column(JSON, nullable=False)
    start_time = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    analyst_id = db.Column(db.Integer, db.ForeignKey('analyst.analyst_id'))


class Worker(db.Model):

    __tablename__ = 'worker'

    worker_id = db.Column(db.Integer, primary_key=True)
    registered_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    last_seen = db.Column(db.DateTime, nullable=False)
    startup_info = db.Column(JSON)


class Command(db.Model):

    __tablename__ = 'command'

    command_id = db.Column(db.Integer, primary_key=True)
    command_name = db.Column(db.String(50), index=True, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    response = db.Column(db.Text, nullable=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.job_id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.worker_id'))
