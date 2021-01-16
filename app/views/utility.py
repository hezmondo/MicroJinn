from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.dao.filter import get_rent_s 
from app.dao.functions import backup_database
from app.dao.utility import delete_record, get_emailaccount, get_emailaccounts, get_rent_ex, post_emailaccount

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
        return redirect(url_for('{}}'.format(redir)))
    

@util_bp.route('/email_accounts', methods=['GET'])
def email_accounts():
    emailaccs = get_emailaccounts()

    return render_template('email_accounts.html', emailaccs=emailaccs)


@util_bp.route('/email_account/<int:id>', methods=['GET', 'POST'])
@login_required
def email_account(id):
    if request.method == "POST":
        id = post_emailaccount(id)
        return redirect(url_for('util_bp.email_account', id=id))

    emailacc = get_emailaccount(id) if id != 0 else {"id": 0}

    return render_template('email_account.html', emailacc=emailacc)


@util_bp.route('/rent_ex/<int:id>', methods=["GET"])
@login_required
def rent_ex(id):
    rent_ex = get_rent_ex(id)

    return render_template('rent_ex.html', rent_ex=rent_ex)


@util_bp.route('/rents_ex', methods=['GET', 'POST'])
def rents_ex():
    filterdict, rent_s = get_rent_s("external", 0)

    return render_template('rents_ex.html', filterdict=filterdict, rent_s=rent_s)
