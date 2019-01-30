from app import db


class Analyst(db.Model):

    __tablename__ = 'analyst'

    analyst_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    salt = db.Column(db.String(255), nullable=False)
    registered_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)


class Command(db.Model):

    __tablename__ = 'command'

    command_id = db.Column(db.Integer, primary_key=True)
    command_name = db.Column(db.String(50), nullable=False)
    arguments = db.Column(db.String(255), nullable=True)
    response = db.Column(db.Text, nullable=True)
    analyst_id = db.Column(db.Integer, db.ForeignKey('analyst.analyst_id'))
