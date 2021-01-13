from flask import Blueprint, render_template, redirect, request, session
from flask_login import login_required
from app.dao.charge import get_charges
from app.dao.common import get_combodict
from app.dao.filter import get_rentobjects
from app.dao.rent_object import get_rent_object, post_rent

ro_bp = Blueprint('ro_bp', __name__)

@ro_bp.route('/rent_object/<int:id>', methods=['GET', 'POST'])
# @login_required
def rent_object(id):
    if request.method == "POST":
        id = post_rent(id)

    combodict = get_combodict("basic")
    rentobject, properties = get_rent_object(id)
    charges = get_charges(id)
    session['mailtodet'] = rentobject.mailtodet
    session['mailaddr'] = rentobject.mailaddr
    session['propaddr'] = rentobject.propaddr
    session['tenantname'] = rentobject.tenantname

    return render_template('rent_object.html', charges=charges, rentobject=rentobject, properties=properties,
                           combodict=combodict)
