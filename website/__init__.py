import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_mail import Mail
from dotenv import load_dotenv

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app():
    app = Flask(__name__)
    load_dotenv()

    app.config['SECRET_KEY'] = 'asd123'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    with app.app_context():
        create_database()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database():
    db_name = os.getenv('DB_NAME')

    if not db_name:
        raise ValueError("DB_NAME environment variable is not set")

    if not path.exists('website/' + db_name):
        db.create_all()
