from flask import Blueprint, redirect, render_template, request
from flask_login import login_required
from app.dao.charge import get_charges, get_charge, post_charge

charge_bp = Blueprint('charge_bp', __name__)


@charge_bp.route('/charge/<int:id>', methods=["GET", "POST"])
@login_required
def charge(id):
    if request.method == "POST":
        rentid = post_charge(id)

        return redirect("/views/rent_/{}".format(rentid))

    charge, chargedescs = get_charge(id)

    return render_template('charge.html', charge=charge, chargedescs=chargedescs)


@charge_bp.route('/charges', methods=['GET', 'POST'])
def charges():
    rentid = request.args.get('rentid', "0", type=str)
    rentcode = request.args.get('rentcode', "", type=str)
    charges = get_charges(rentid)

    return render_template('charges.html', charges=charges, rentid=rentid, rentcode=rentcode)


