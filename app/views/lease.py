from flask import Blueprint, redirect, render_template,  request, url_for
from flask_login import login_required
from app.dao.lease import get_lease, get_leases, post_lease

lease_bp = Blueprint('lease_bp', __name__)

@lease_bp.route('/lease/<int:lease_id>', methods=['GET', 'POST'])
@login_required
def lease(lease_id):
    if request.method == "POST":
        rent_id = post_lease(lease_id)
        return redirect(url_for('bp_rent.rent_', rent_id=rent_id))
    lease, uplift_types = get_lease(lease_id)
    return render_template('lease.html', lease=lease, uplift_types=uplift_types)


@lease_bp.route('/leases', methods=['GET', 'POST'])
def leases():
    leases, uplift_types, rcd, uld, ult = get_leases()

    return render_template('leases.html', leases=leases, uplift_types=uplift_types, rcd=rcd, uld=uld, ult=ult)

