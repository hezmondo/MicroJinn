from flask import Blueprint, render_template, redirect, request, url_for
from app.main.common import get_combodict_rent
from app.main.rent import get_rentp, get_rent_strings, rent_validation, update_rent_rem, update_tenant

rent_bp = Blueprint('rent_bp', __name__)


@rent_bp.route('/rent/<int:rent_id>', methods=['GET', 'POST'])
# @login_required
def rent(rent_id):
    message = request.args.get('message', '', type=str)
    if request.method == "POST":
        rent_id = update_rent_rem(rent_id)
        return redirect(url_for('rent_bp.rent', rent_id=rent_id))
    combodict = get_combodict_rent()
    # gather rent combobox values
    rent = get_rentp(rent_id) if rent_id != 0 else {"id": 0}    # get full enhanced rent pack
    # basic validation check for mail and email variables
    messages = rent_validation(rent, message)
    rentstats = get_rent_strings(rent, 'rent')

    return render_template('rent.html', rent=rent, combodict=combodict, rentstats=rentstats, messages=messages)


@rent_bp.route('/tenant/<int:rent_id>', methods=['GET', 'POST'])
# @login_required
def tenant(rent_id):
    update_tenant(rent_id)

    return redirect(url_for('rent_bp.rent', rent_id=rent_id))
