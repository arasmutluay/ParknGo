from flask import Blueprint, flash, redirect, url_for, session, render_template, request
from flask_login import current_user, logout_user, login_required, login_user
from email_validator import validate_email, EmailNotValidError

from website import db
from website.models import User

auth = Blueprint('auth', __name__)


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        flash("Access Denied: First you need to logout before signing up!", 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        birthDate = request.form.get('birthDate')
        user = User.query.filter_by(email=email).first()

        try:
            validate = validate_email(email)
            email = validate["email"]
        except EmailNotValidError as e:
            flash('Please enter a valid email!', category='error')
            return render_template("sign_up.html", user=current_user)

        if user:
            flash('Email already exists!', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')

        else:
            new_user = User(email=email, firstName=firstName,
                            password=password1, birthDate=birthDate, role='user')
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)


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
            if user.password == password:
                login_user(user, remember=True)
                flash('Logged in', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again!', category='error')
        else:
            flash('Email does not exist!', category='error')

    return render_template("login.html", user=current_user)



@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('views.home'))
