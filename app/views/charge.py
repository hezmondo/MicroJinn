from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.dao.charge import post_charge
from app.main.charge import mget_charge, mget_charges

charge_bp = Blueprint('charge_bp', __name__)


@charge_bp.route('/charge/<int:charge_id>', methods=["GET", "POST"])
@login_required
def charge(charge_id):
    if request.method == "POST":
        rent_id = post_charge(charge_id)

        return redirect(url_for('rent_bp.rent', rent_id=rent_id))

    charge, chargedescs = mget_charge(charge_id)

    return render_template('charge.html', charge=charge, chargedescs=chargedescs)


@charge_bp.route('/charges', methods=['GET', 'POST'])
def charges():
    rent_id = request.args.get('rent_id', "0", type=str)
    rentcode = request.args.get('rentcode', "", type=str)
    charges = mget_charges(rent_id)

    return render_template('charges.html', charges=charges, rent_id=rent_id, rentcode=rentcode)


