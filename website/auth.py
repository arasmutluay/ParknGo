from flask import Blueprint, flash, redirect, url_for, session, render_template, request, current_app
from flask_login import current_user, logout_user, login_required, login_user
from email_validator import validate_email, EmailNotValidError
from email.message import EmailMessage
import ssl
import smtplib

from itsdangerous import URLSafeTimedSerializer

from website import db
from website.models import User

auth = Blueprint('auth', __name__)


def send_email(email_reciever, subject, body):
    email_sender = 'aras.mutluay99@gmail.com'
    email_password = 'jizo cyzj zjrx ymvl'

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_reciever
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_reciever, em.as_string())

    return "Message sent!"


def generate_token(email):
    secret_key = 'secret_key'
    serializer = URLSafeTimedSerializer(secret_key)
    token = serializer.dumps(email, salt='email-confirm')

    return token


def verify_token(token):
    secret_key = 'secret_key'
    serializer = URLSafeTimedSerializer(secret_key)

    try:
        email = serializer.loads(token, salt='email-confirm',
                                 max_age=3600)
        return email
    except Exception as e:
        return None


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        flash("Access Denied: First you need to logout before signing up!", 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        birth_date = request.form.get('birth_date')
        country = request.form.get('country')
        city = request.form.get('city')
        gender = request.form.get('gender')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')

        try:
            validate = validate_email(email)
            email = validate["email"]
        except EmailNotValidError as e:
            flash('Please enter a valid email!', category='error')
            return render_template("signup.html", user=current_user)

        session['new_user'] = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'birth_date': birth_date,
            'country': country,
            'city': city,
            'gender': gender,
            'address': address,
            'phone_number': phone_number,
            'role': 'user'
        }

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists!', category='error')

        else:
            token = generate_token(email)
            subject = 'Create a Password'
            body = f'Please click the link below to create a password: {url_for("auth.create_password", token=token, _external=True)}'
            send_email(email, subject, body)

            flash('An email has been sent with a link to create your password.', category='success')
            return redirect(url_for('auth.sign_up'))

    return render_template("signup.html", user=current_user)


@auth.route('/create_password/<token>', methods=['GET', 'POST'])
def create_password(token):
    if request.method == 'POST':
        email = verify_token(token)

        if email:
            user_details = session.pop('new_user', None)
            if user_details:
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')

                if password != confirm_password:
                    flash('Passwords do not match.', category='error')
                    return redirect(url_for('auth.create_password', token=token))

                new_user = User(**user_details)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()

                flash('Password successfully set. You can now login.', category='success')
                return redirect(url_for('auth.login'))
            else:
                flash('User details not found in the session.', category='error')
        else:
            flash('Invalid token.', category='error')

        return redirect(url_for('auth.login'))

    return render_template('create_password.html', token=token)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("Access Denied: First you need to logout before signing up!", 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user:
            if user.check_password(password):
                login_user(user, remember=True)
                flash('Logged in', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again!', category='danger')
        else:
            flash('Email does not exist!', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if not current_user.is_authenticated:
        flash("Access Denied: First you need to login before changing password.", 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        user = current_user

        if new_password == old_password:
            flash("Error: New password cannot be the same as your old password.", 'error')
            return redirect(url_for('auth.change_password'))

        if old_password != user.password:
            flash("Error: Incorrect old password. Please try again.", 'error')
            return redirect(url_for('auth.change_password'))

        user.password = new_password
        db.session.commit()

        flash("Password changed successfully!", 'success')
        return redirect(url_for('auth.change_password'))

    return render_template("change_password.html", user=current_user)


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        flash("Access Denied: First you need to logout before using the forgot password", 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        token = generate_token(email)
        subject = 'Reset Your Password'
        body = f'Please click the link below to reset your password: {url_for("auth.set_new_password", token=token, _external=True)}'
        send_email(email, subject, body)

        flash('An email has been sent with a link to reset your password.', category='success')
        return redirect(url_for('views.home'))

    return render_template("forgot_password.html", user=current_user)


@auth.route('/set_new_password/<token>', methods=['GET', 'POST'])
def set_new_password(token):
    if request.method == 'POST':
        email = verify_token(token)

        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', category='error')
            return redirect(url_for('/set_new_password/<token>', token=token))

        user = User.query.filter_by(email=email).first()
        user.set_password(password)
        db.session.commit()

        flash('Password changed successfully. You can now log in with your new password.', category='success')
        return redirect(url_for('auth.login'))

    return render_template('set_new_password.html', user=current_user, token=token)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('views.home'))
