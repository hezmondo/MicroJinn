from flask import Blueprint, render_template,  request
from flask_login import login_required
from app.dao.filter import get_rentobjects
from app.dao.rent_external import get_rent_external

rx_bp = Blueprint('rx_bp', __name__)

@rx_bp.route('/rent_external/<int:id>', methods=["GET"])
@login_required
def rent_external(id):
    rent_external = get_rent_external(id)

    return render_template('rent_external.html', rent_external=rent_external)

@rx_bp.route('/rents_external', methods=['GET', 'POST'])
def rents_external():
    filterdict, rentobjects = get_rentobjects("external", 0)

    return render_template('rents_external.html', filterdict=filterdict, rentobjects=rentobjects)
