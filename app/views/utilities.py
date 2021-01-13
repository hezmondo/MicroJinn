from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.dao.delete import delete_record
from app.dao.functions import backup_database

ut_bp = Blueprint('ut_bp', __name__)

@ut_bp.route('/backup', methods=['GET', 'POST'])
# @login_required
def backup():
    if request.method == "POST":
        backup_database()

    return render_template('backup.html')

@ut_bp.route('/delete_item/<int:id>')
@login_required
def delete_item(id):
    redir, rentid = delete_record(id)

    return redirect(url_for('{}'.format(redir)))
