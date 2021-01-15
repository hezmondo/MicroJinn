from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required
from app.dao.charge import get_charges
from app.dao.common import get_combodict
from app.dao.rent_object import get_rent_object, post_rent

ro_bp = Blueprint('ro_bp', __name__)

@ro_bp.route('/rent_object/<int:id>', methods=['GET', 'POST'])
# @login_required
def rent_object(id):
    if request.method == "POST":
        id = post_rent(id)
        return redirect(url_for('re_bp.rent_object', id=id))

    combodict = get_combodict("basic")
    rentobject = get_rent_object(id) if id != 0 else {"id": 0}
    charges = get_charges(id) if id != 0 else None

    return render_template('rent_object.html', charges=charges, rentobject=rentobject, combodict=combodict)
