from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.dao.rental import get_rental, getrentals, get_rentalstatement, post_rental

rental_bp = Blueprint('rental_bp', __name__)

@rental_bp.route('/rentals', methods=['GET', 'POST'])
def rentals():
    rentals, rentsum = getrentals()

    return render_template('rentals.html', rentals=rentals, rentsum=rentsum)


@rental_bp.route('/rental/<int:rental_id>', methods=['GET', 'POST'])
# @login_required
def rental(rental_id):
    if request.method == "POST":
        rental_id = post_rental(rental_id)
        return redirect(url_for('rental_bp.rental', rental_id=rental_id))

    rental = get_rental(rental_id)

    return render_template('rental.html', rental=rental)


@rental_bp.route('/rental_statement/<int:rental_id>', methods=["GET", "POST"])
# @login_required
def rental_statement(rental_id):
    rentalstatement = get_rentalstatement(rental_id)

    return render_template('rental_statement.html', rentalstatement=rentalstatement)
