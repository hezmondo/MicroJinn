from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.dao.charge import get_charges, get_charge, post_charge

charge_bp = Blueprint('charge_bp', __name__)


@charge_bp.route('/charge/<int:charge_id>', methods=["GET", "POST"])
@login_required
def charge(charge_id):
    if request.method == "POST":
        rent_id = post_charge(charge_id)

        return redirect("/views/rent/{}".format(rent_id))

    charge, chargedescs = get_charge(charge_id)

    return render_template('charge.html', charge=charge, chargedescs=chargedescs)


@charge_bp.route('/charges', methods=['GET', 'POST'])
def charges():
    rent_id = request.args.get('rent_id', "0", type=str)
    rentcode = request.args.get('rentcode', "", type=str)
    charges = get_charges(rent_id)

    return render_template('charges.html', charges=charges, rent_id=rent_id, rentcode=rentcode)


