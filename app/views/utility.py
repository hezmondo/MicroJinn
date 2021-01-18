from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.dao.functions import backup_database
from app.dao.main import delete_record\

util_bp = Blueprint('util_bp', __name__)


@util_bp.route('/backup', methods=['GET', 'POST'])
# @login_required
def backup():
    if request.method == "POST":
        backup_database()

    return render_template('backup.html')


@util_bp.route('/delete_item/<int:id>')
@login_required
def delete_item(id):
    redir, id_2 = delete_record(id)
    if id_2:
        return redirect("/{}/{}".format(redir, id_2))
    else:
        return redirect(url_for('{}'.format(redir)))
