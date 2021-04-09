from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.main.headrent import get_headrents_p, mget_headrent, update_landlord, update_headrent, \
    update_propaddr, update_note

headrent_bp = Blueprint('headrent_bp', __name__)


@headrent_bp.route('/headrents', methods=['GET', 'POST'])
def headrents():
    filterdict, headrents = get_headrents_p()

    return render_template('headrents.html', filterdict=filterdict, headrents=headrents)


@headrent_bp.route('/headrent/<int:headrent_id>', methods=["GET", "POST"])
@login_required
def headrent(headrent_id):
    message = request.args.get('message', '', type=str)
    if request.method == "POST":
        update_headrent(headrent_id)
        return redirect(url_for('headrent_bp.headrent', headrent_id=headrent_id))
    headrent = mget_headrent(headrent_id)

    return render_template('headrent.html', headrent=headrent, message=message)


# update headrent details from headrent page based on action
@headrent_bp.route('/headrent_update/<int:headrent_id>', methods=['GET', 'POST'])
@login_required
def headrent_update(headrent_id):
    action = request.args.get('action', type=str)
    message = ''
    try:
        if action == 'landlord':
            update_landlord(headrent_id)
        if action == 'property':
            update_propaddr(headrent_id)
        if action == 'note':
            update_note(headrent_id)
    except Exception as ex:
        message = f"Update headrent failed. Error:  {str(ex)}"

    return redirect(url_for('headrent_bp.headrent', headrent_id=headrent_id, message=message))
