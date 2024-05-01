from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON
from my_app import db, manager


class User (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    pet_name = db.Column(db.String(255), nullable=True)
    number_of_calculations = db.Column(db.Integer, nullable=True, default=0)


class UserResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    json_result = db.Column(JSON, nullable=False)
    user = db.relationship('User', backref=db.backref('results', lazy=True))


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
