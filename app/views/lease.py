from flask import Blueprint, redirect, render_template,  request
from flask_login import login_required
from app.dao.lease import get_lease, get_leases, post_lease

le_bp = Blueprint('le_bp', __name__)

@le_bp.route('/lease/<int:id>', methods=['GET', 'POST'])
@login_required
def lease(id):
    # id can be actual lease id or 0 (for new lease or for id unknown as coming from rent)
    if request.method == "POST":
        rentid = post_lease(id)

        return redirect('/rent_object/{}'.format(rentid))

    action, lease, uplift_types = get_lease(id)

    return render_template('lease.html', action=action, lease=lease, uplift_types=uplift_types)


@le_bp.route('/leases', methods=['GET', 'POST'])
def leases():
    leases, uplift_types, rcd, uld, ult = get_leases()

    return render_template('leases.html', leases=leases, uplift_types=uplift_types, rcd=rcd, uld=uld, ult=ult)

