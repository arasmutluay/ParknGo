from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(30))
    firstName = db.Column(db.String(50))
    birthDate = db.Column(db.DateTime)
    role = db.Column(db.String(10))
