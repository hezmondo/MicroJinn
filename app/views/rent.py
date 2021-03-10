from flask import Blueprint, render_template, redirect, request, url_for
from app.dao.charge import get_charges
from app.main.common import get_combodict_rent, inc_date_m
from app.dao.rent import get_rent, post_rent, update_tenant
from app.main.rent import get_rent_strings, rent_validation

rent_bp = Blueprint('rent_bp', __name__)


@rent_bp.route('/rent/<int:rent_id>', methods=['GET', 'POST'])
# @login_required
def rent(rent_id):
    message = request.args.get('message', '', type=str)
    if request.method == "POST":
        rent_id = post_rent(rent_id)
        return redirect(url_for('rent_bp.rent', rent_id=rent_id))
    combodict = get_combodict_rent()
    # gather rent combobox values
    rent = get_rent(rent_id) if rent_id != 0 else {"id": 0}
    # basic validation check for mail and email variables
    messages = rent_validation(rent, message)
    charges = get_charges(rent_id) if rent_id != 0 else None
    rentstats = get_rent_strings(rent, 'rent')

    return render_template('rent.html', charges=charges, rent=rent, combodict=combodict,
                           rentstats=rentstats, messages=messages)


@rent_bp.route('/tenant/<int:rent_id>', methods=['GET', 'POST'])
# @login_required
def tenant(rent_id):
    update_tenant(rent_id)

    return redirect(url_for('rent_bp.rent', rent_id=rent_id))
