from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.dao.headrent import get_headrent
from app.main.common import get_combodict_basic
from app.main.headrent import get_headrents_p, update_headrent
from app.modeltypes import HrStatuses

headrent_bp = Blueprint('headrent_bp', __name__)


@headrent_bp.route('/headrents', methods=['GET', 'POST'])
def headrents():
    filterdict, headrents = get_headrents_p()

    return render_template('headrents.html', filterdict=filterdict, headrents=headrents)


@headrent_bp.route('/headrent/<int:headrent_id>', methods=["GET", "POST"])
@login_required
def headrent(headrent_id):
    if request.method == "POST":
        update_headrent(headrent_id)
        return redirect(url_for('headrent_bp.headrent', headrent_id=headrent_id))
    headrent = get_headrent(headrent_id)
    headrent.status = HrStatuses.get_name(headrent.status_id)
    combodict = get_combodict_basic()

    return render_template('headrent.html', combodict=combodict, headrent=headrent)
