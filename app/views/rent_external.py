from flask import Blueprint, render_template,  request
from flask_login import login_required
from app.dao.filter import get_rent_s
from app.dao.rent_external import get_rent_external

rentx_bp = Blueprint('rentx_bp', __name__)

@rentx_bp.route('/rent_external/<int:id>', methods=["GET"])
@login_required
def rent_external(id):
    rent_external = get_rent_external(id)

    return render_template('rent_external.html', rent_external=rent_external)

@rentx_bp.route('/rents_external', methods=['GET', 'POST'])
def rents_external():
    filterdict, rent_s = get_rent_s("external", 0)

    return render_template('rents_external.html', filterdict=filterdict, rent_s=rent_s)
