from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required
from app.dao.charge import get_charges
from app.dao.common import get_combodict_rent
from app.dao.rent import get_rent, post_rent, update_tenant
from app.main.rent import get_rent_strings

rent_bp = Blueprint('rent_bp', __name__)


@rent_bp.route('/rent/<int:rent_id>', methods=['GET', 'POST'])
# @login_required
def rent(rent_id):
    if request.method == "POST":
        rent_id = post_rent(rent_id)

        return redirect(url_for('rent_bp.rent', rent_id=rent_id))

    combodict = get_combodict_rent()
    # gather rent combobox values
    rent = get_rent(rent_id) if rent_id != 0 else {"id": 0}
    charges = get_charges(rent_id) if rent_id != 0 else None
    rentstats = get_rent_strings(rent, 'rent')

    return render_template('rent.html', charges=charges, rent=rent, combodict=combodict, rentstats=rentstats)


@rent_bp.route('/tenant/<int:rent_id>', methods=['GET', 'POST'])
# @login_required
def tenant(rent_id):
    update_tenant(rent_id)

    return redirect(url_for('rent_bp.rent', rent_id=rent_id))
