from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required
from app.dao.charge import get_charges
from app.dao.common import get_combodict
from app.dao.rent_ import get_rent_, post_rent

rent_bp = Blueprint('rent_bp', __name__)


@rent_bp.route('/rent_/<int:id>', methods=['GET', 'POST'])
# @login_required
def rent_(id):
    if request.method == "POST":
        id = post_rent(id)
        return redirect(url_for('rental_bp.rent_', id=id))

    combodict = get_combodict("basic")
    rent_ = get_rent_(id) if id != 0 else {"id": 0}
    charges = get_charges(id) if id != 0 else None

    return render_template('rent_.html', charges=charges, rent_=rent_, combodict=combodict)
