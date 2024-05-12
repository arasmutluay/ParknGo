from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from flask_login import UserMixin

# Associations
reservations = db.Table(
    'reservations',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('carpark_id', db.Integer, db.ForeignKey('carparks.id'), primary_key=True),
)


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
    status = db.Column(db.String, default='active')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Carpark(db.Model, UserMixin):
    __tablename__ = 'carparks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    company = db.Column(db.String(30))
    location = db.Column(db.String(30))
    price = db.Column(db.Integer)
    max_allowed_capacity = db.Column(db.Integer)
    remaining_capacity = db.Column(db.Integer, default=max_allowed_capacity)
    max_total_capacity = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String, default='active')
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_action_date = db.Column(db.DateTime, default=datetime.utcnow)
