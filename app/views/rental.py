from flask import Blueprint, redirect, render_template,  request
from flask_login import login_required
from app.dao.rental import get_rental, getrentals, get_rentalstatement, post_rental

rental_bp = Blueprint('rental_bp', __name__)

@rental_bp.route('/rentals', methods=['GET', 'POST'])
def rentals():
    rentals, rentsum = getrentals()

    return render_template('rentals.html', rentals=rentals, rentsum=rentsum)


@rental_bp.route('/rental/<int:id>', methods=['GET', 'POST'])
# @login_required
def rental(id):
    if request.method == "POST":
        id = post_rental(id)

        return redirect('/rental/{}'.format(id))

    rental, advarrdets, freqdets = get_rental(id)

    return render_template('rental.html', rental=rental, advarrdets=advarrdets, freqdets=freqdets)


@rental_bp.route('/rental_statement/<int:id>', methods=["GET", "POST"])
# @login_required
def rental_statement(id):
    rentalstatem = get_rentalstatement()
    print("rentalstatem")
    print(rentalstatem)

    return render_template('rental_statement.html', rentalstatem=rentalstatem)
