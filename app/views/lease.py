from flask import Blueprint, redirect, render_template,  request, url_for
from flask_login import login_required
from app.main.lease import mget_lease_info, mget_leases, update_lease

lease_bp = Blueprint('lease_bp', __name__)

@lease_bp.route('/lease/<int:lease_id>', methods=['GET', 'POST'])
@login_required
def lease(lease_id):
    if request.method == "POST":
        rent_id = update_lease()
        return redirect(url_for('rent_bp.rent', rent_id=rent_id))
    lease, methods = mget_lease_info(lease_id)

    return render_template('lease.html', lease=lease, methods=methods)


@lease_bp.route('/leases', methods=['GET', 'POST'])
def leases():
    leases, rentcode, days, method = mget_leases()

    return render_template('leases.html', leases=leases, rentcode=rentcode, days=days, method=method)

