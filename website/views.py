from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from .models import User, Carpark, reservations
from website import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated and current_user.role == 'admin':

        total_end_users = User.query.count()
        active_end_users = User.query.filter_by(status='active').count()
        inactive_end_users = User.query.filter_by(status='inactive').count()
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
    else:

        return render_template("home.html", user=current_user)


@views.route('/search_carpark', methods=['GET', 'POST'])
def search_carpark():
    distinct_locations = Carpark.query.with_entities(Carpark.location).distinct().all()
    print("Distinct locations:", distinct_locations)

    return render_template("search_carpark.html", user=current_user,
                           distinct_locations=distinct_locations)


@views.route('/search_results', methods=['GET', 'POST'])
def search_results():
    page = request.args.get('page', 1, type=int)
    rows_per_page = 3

    car_parks = Carpark.query.paginate(page=page, per_page=rows_per_page)

    if not car_parks:
        flash('No results found.', category='error')
        return redirect(url_for('views.home'))

    return render_template("search_results.html", car_parks=car_parks, user=current_user)


@views.route('/create_reservation/<int:car_park_id>', methods=['GET', 'POST'])
def create_reservation(car_park_id):
    if request.method == 'POST':
        user_id = current_user.id
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if not user_id:
            flash('User ID is required.', 'error')
            return redirect(url_for('views.create_reservation', car_park_id=car_park_id))

        existing_attempt = db.session.query(reservations).filter_by(
            user_id=user_id, car_park_id=car_park_id).first()

        if existing_attempt:
            flash('The reservation has already been created.', 'error')
            return redirect(url_for('views.search_carpark', user=current_user, car_park_id=car_park_id))

        car_park = Carpark.query.filter_by(id=car_park_id).first()
        car_park.last_action_date = datetime.now()

        new_reservation = reservations.insert().values(user_id=user_id, car_park_id=car_park_id)
        db.session.execute(new_reservation)
        db.session.commit()

        flash('Reservation created successfully.', 'success')
        return redirect(url_for('views.home'))
    else:
        car_park = Carpark.query.get_or_404(car_park_id)
        return render_template("create_reservation.html", user=current_user,
                               car_park=car_park)


@views.route('/carpark_list', methods=['GET', 'POST'])
def carpark_list():
    if not current_user.is_authenticated and current_user.role == 'admin':
        flash("Access Denied: First you need to be logged in as an Admin!.", 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        car_park_id = request.form.get('car_park_id')
        action = request.form.get('action')

        if action == 'block':
            block_carpark(car_park_id)
            flash("Car park blocked successfully!", 'success')
        elif action == 'unblock':
            unblock_carpark(car_park_id)
            flash("Car park unblocked successfully!", 'success')

        return redirect(url_for('views.carpark_list'))

    page = request.args.get('page', 1, type=int)
    rows_per_page = 3

    car_parks = Carpark.query.paginate(page=page, per_page=rows_per_page)

    return render_template("carpark_list.html", user=current_user,
                           car_parks=car_parks)


@views.route('/profile', methods=['GET'])
def profile():
    return render_template("profile.html", user=current_user)


@views.route('/carpark_details', methods=['GET', 'POST'])
def carpark_details():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash("Access Denied: First you need to be logged in as an Admin!", 'error')
        return redirect(url_for('views.home'))

    car_park_id = request.form.get('car_park_id')
    car_park = Carpark.query.filter_by(id=car_park_id).first()

    if request.method == 'POST':

        if car_park:
            if request.form.get('action') == 'block':
                block_carpark(car_park.id)
                flash("Car park blocked successfully!", 'success')
            elif request.form.get('action') == 'unblock':
                unblock_carpark(car_park.id)
                flash("Car park unblocked successfully!", 'success')
        else:
            flash("Car park not found.", "error")
            return redirect(url_for('views.carpark_list'))

    return render_template("carpark_details.html", user=current_user,
                           car_park=car_park,
                           car_park_id=car_park_id)


@views.route('/update_carpark', methods=['POST'])
def update_carpark():
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash("Access Denied: First you need to be logged in as an Admin!", 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        car_park_id = request.form.get('carpark_id')
        car_park = Carpark.query.get(car_park_id)

        if not car_park:
            flash("Car park not found.", "error")
            return redirect(url_for('views.carpark_list'))

        car_park.name = request.form.get('name')
        car_park.company = request.form.get('company')
        car_park.location = request.form.get('location')
        car_park.price = request.form.get('price')
        car_park.max_allowed_capacity = request.form.get('max_allowed_capacity')
        car_park.max_total_capacity = request.form.get('max_total_capacity')
        car_park.last_action_date = datetime.now()

        db.session.commit()

        flash("Car park information updated successfully!", 'success')

    return redirect(url_for('views.carpark_list'))


def block_carpark(carpark_id):
    car_park = Carpark.query.get(carpark_id)
    if car_park:
        if car_park.status != "blocked":
            car_park.status = "blocked"
            car_park.last_action_date = datetime.now()
            db.session.commit()
        else:
            flash("Car park is already blocked.", "warning")
    else:
        flash("Car park not found.", "error")


def unblock_carpark(carpark_id):
    car_park = Carpark.query.get(carpark_id)
    if car_park:
        if car_park.status != "active":
            car_park.status = "active"
            car_park.last_action_date = datetime.now()
            db.session.commit()
        else:
            flash("Car park is already unblocked.", "warning")
    else:
        flash("Car park not found.", "error")


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
