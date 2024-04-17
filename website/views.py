from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from .models import User, Carpark
from website import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    # user queries
    total_end_users = User.query.count()
    active_end_users = User.query.filter_by(status='active').count()
    inactive_end_users = User.query.filter_by(status='inactive').count()

    # Carpark queries
    total_car_parks = Carpark.query.count()
    active_car_parks = Carpark.query.filter_by(status='active').count()
    blocked_car_parks = Carpark.query.filter_by(status='blocked').count()

    return render_template("home.html", user=current_user,
                           total_end_users=total_end_users,
                           active_end_users=active_end_users,
                           inactive_end_users=inactive_end_users,
                           total_car_parks=total_car_parks,
                           active_car_parks=active_car_parks,
                           blocked_car_parks=blocked_car_parks)


@views.route('/carpark_list', methods=['GET'])
def carpark_list():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    car_parks = Carpark.query.paginate(page=page, per_page=per_page)

    return render_template("carpark_list.html", user=current_user,
                           car_parks=car_parks)


@views.route('/create_carpark', methods=['GET', 'POST'])
def create_carpark():
    if not current_user.is_authenticated:
        flash("Access Denied: First you need to login before creating a Car Park!", 'error')
        return redirect(url_for('views.home'))

    if current_user.role != 'admin':
        flash("Access Denied: Only Admin can create a Car Park!")
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        name = request.form.get('name')
        company = request.form.get('company')
        location = request.form.get('location')
        price = request.form.get('price')
        max_allowed_capacity = request.form.get('max_allowed_capacity')
        max_total_capacity = request.form.get('max_total_capacity')

        carpark_name = Carpark.query.filter_by(name=name).first()

        if carpark_name:
            flash('Car Park already exists!', category='error')
        elif int(price) < 0:
            flash('Please enter a correct price for the Car Park!', category='error')
        elif int(max_allowed_capacity) <= 0 or int(max_total_capacity) <= 0:
            flash('Please enter an allowed capacity or total capacity!', category='error')



        else:

            new_carpark = Carpark(name=name,
                                  company=company,
                                  location=location,
                                  price=price,
                                  max_allowed_capacity=max_allowed_capacity,
                                  remaining_capacity=max_allowed_capacity,
                                  max_total_capacity=max_total_capacity)

            db.session.add(new_carpark)
            db.session.commit()

            flash('Car Park is created successfully.', category='success')
            return redirect(url_for('views.home'))

    return render_template("create_carpark.html", user=current_user)
