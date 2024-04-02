from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    birth_date = db.Column(db.DateTime)
    country = db.Column(db.String(30))
    city = db.Column(db.String(30))
    gender = db.Column(db.String(30))
    address = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    role = db.Column(db.String(10))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
